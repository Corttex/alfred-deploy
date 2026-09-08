"""
ALFRED Edge Worker (Nó Local do Windows)
Roda 24/7 no seu PC local e se conecta ao Nó Mestre (Hetzner) via WebSocket.
Recebe instruções para executar comandos nativamente no seu Windows.
"""
import asyncio
import websockets
import json
import subprocess
import os

# Quando subir para o Hetzner, troque para 'wss://alfred.seudominio.com/ws/worker/windows-pc'
MASTER_NODE_URL = "ws://127.0.0.1:8000/ws/worker/windows-pc"
ALFRED_TOKEN = "test-token" # O mesmo configurado no seu .env

async def execute_local_command(command: str):
    """Executa um comando localmente no Windows e retorna o output."""
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True
        )
        stdout, stderr = await process.communicate()
        
        return {
            "status": "success" if process.returncode == 0 else "error",
            "output": stdout.decode("utf-8", errors="ignore").strip(),
            "error": stderr.decode("utf-8", errors="ignore").strip(),
            "returncode": process.returncode
        }
    except Exception as e:
        return {"status": "critical_error", "error": str(e)}

async def worker_loop():
    url_with_token = f"{MASTER_NODE_URL}?token={ALFRED_TOKEN}"
    print(f"[EDGE WORKER] Tentando conectar ao Nó Mestre em: {MASTER_NODE_URL}...")
    
    while True:
        try:
            async with websockets.connect(url_with_token) as ws:
                print("✅ Conectado à Mente de Colmeia (Nó Mestre)!")
                
                while True:
                    # Aguarda ordens do servidor
                    message = await ws.recv()
                    payload = json.loads(message)
                    
                    if payload.get("event") == "execute_command":
                        cmd = payload.get("command")
                        print(f"\n⚡ Recebida Ordem de Execução: {cmd}")
                        
                        # Executa o comando no PC Windows
                        result = await execute_local_command(cmd)
                        
                        # Devolve o resultado pro servidor
                        response = {
                            "event": "command_result",
                            "task_id": payload.get("task_id"),
                            "result": result
                        }
                        await ws.send(json.dumps(response))
                        print(f"📤 Resultado enviado de volta ao Mestre.")
                        
        except websockets.exceptions.ConnectionClosed:
            print("⚠️ Conexão perdida. Tentando reconectar em 5 segundos...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"❌ Erro de conexão: {e}. Retentando em 5 segundos...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(worker_loop())
