import os
import paramiko
import logging
from dotenv import load_dotenv

load_dotenv()

def execute_ssh_command(command: str) -> str:
    """
    Executa um comando na VPS (Hetzner) de forma segura.
    Não tocar nas instâncias do Coolify a menos que explicitamente solicitado!
    """
    host = os.getenv("VPS_01_HOST")
    user = os.getenv("VPS_01_USER", "root")
    password = os.getenv("VPS_01_PASSWORD")

    if not host or not password:
        return "Erro: Credenciais SSH da Hetzner não configuradas no .env."

    logging.info(f"Conectando via SSH em {user}@{host} para executar: {command}")
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=user, password=password, timeout=10)
        
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        
        client.close()
        
        if error and not output:
            return f"Erro na execução remota: {error}"
            
        return output if output else "Comando executado com sucesso (sem saída)."
        
    except Exception as e:
        return f"Falha crítica no SSH: {str(e)}"

def get_server_status() -> str:
    """
    Função engatilhada pelo botão 'Analisar Hetzner'.
    Traz o status da RAM e uso de CPU.
    """
    command = "free -m | awk 'NR==2{printf \"RAM Usage: %s/%sMB (%.2f%%)\", $3,$2,$3*100/$2 }' && echo '' && top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
    return execute_ssh_command(command)
