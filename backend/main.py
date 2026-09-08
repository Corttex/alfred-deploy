"""
A.L.F.R.E.D. — Orchestrator Core
Ponto de entrada principal. FastAPI + WebSocket.
"""

import json
import uuid
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from router import TaskRouter
from models import Task, TaskStatus
# Removed old imports for now
# from memory.rag import memory_bank
# from telegram_bot import start_telegram_bot
# from memory.watcher import start_watcher
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[A.L.F.R.E.D.] Orquestrador iniciado em ws://{settings.HOST}:{settings.PORT}")
    
    yield
    print("[A.L.F.R.E.D.] Desligando...")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="A.L.F.R.E.D. Orchestrator", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

router = TaskRouter()


class ConnectionManager:
    def __init__(self):
        self.active: dict[str, WebSocket] = {}

    async def connect(self, ws: WebSocket, client_id: str):
        await ws.accept()
        self.active[client_id] = ws

    def disconnect(self, client_id: str):
        self.active.pop(client_id, None)

    async def send(self, client_id: str, data: dict):
        ws = self.active.get(client_id)
        if ws:
            await ws.send_json(data)

    async def broadcast(self, data: dict):
        for ws in self.active.values():
            await ws.send_json(data)

manager = ConnectionManager()
worker_manager = ConnectionManager()


# ── WebSocket Principal ───────────────────────────────────────────────────────
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, token: str = ""):
    if token != settings.effective_token:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    await manager.connect(websocket, client_id)
    await manager.send(client_id, {"event": "connected", "alfred": "Online. Pronto para executar."})

    try:
        while True:
            raw = await websocket.receive_text()
            payload = json.loads(raw)

            task = Task(
                id=str(uuid.uuid4()),
                command=payload.get("command", ""),
                context=payload.get("context", {}),
                client_id=client_id,
                timestamp=datetime.utcnow().isoformat(),
            )

            # Resposta imediata de ACK
            await manager.send(client_id, {
                "event": "task_received",
                "task_id": task.id,
                "message": f"Entendido. Processando: '{task.command[:60]}...'"
            })

            # Executa a tarefa de forma assíncrona e envia resultado
            result = await router.execute(task)

            await manager.send(client_id, {
                "event": "task_complete",
                "task_id": task.id,
                "status": result.status,
                "output": result.output,
                "agent_used": result.agent_used,
            })

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except json.JSONDecodeError:
        await manager.send(client_id, {"event": "error", "message": "JSON inválido."})


# ── WebSocket de Workers (Nós Locais / Edge) ──────────────────────────────────
@app.websocket("/ws/worker/{client_id}")
async def worker_websocket_endpoint(websocket: WebSocket, client_id: str, token: str = ""):
    if token != settings.effective_token:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    await worker_manager.connect(websocket, client_id)
    print(f"[EDGE NODE] Worker '{client_id}' conectado!")
    
    try:
        while True:
            # Mantém a conexão aberta aguardando resultados das tarefas despachadas
            raw = await websocket.receive_text()
            payload = json.loads(raw)
            print(f"[EDGE NODE - {client_id}] Resposta: {payload}")
            
    except WebSocketDisconnect:
        worker_manager.disconnect(client_id)
        print(f"[EDGE NODE] Worker '{client_id}' desconectado.")
    except Exception as e:
        worker_manager.disconnect(client_id)


# ── REST: Health Check ────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {
        "status": "online",
        "alfred": "A.L.F.R.E.D. v1.0",
        "connections": len(manager.active),
        "timestamp": datetime.utcnow().isoformat(),
    }


# ── REST: Disparar tarefa via HTTP (para automações/cron) ─────────────────────
@app.post("/task")
async def http_task(payload: dict, x_alfred_token: str = Header(None)):
    if x_alfred_token != settings.effective_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    task = Task(
        id=str(uuid.uuid4()),
        command=payload.get("command", ""),
        context=payload.get("context", {}),
        client_id="http",
        timestamp=datetime.utcnow().isoformat(),
    )

    result = await router.execute(task)
    return {"task_id": task.id, "status": result.status, "output": result.output}


# ── REST: Telemetria e Comportamento (Chrome Extension) ───────────────────────
@app.post("/api/telemetry")
async def receive_telemetry(payload: dict):
    text = payload.get("text", "")
    url = payload.get("url", "")
    
    if text.strip():
        # Avisa todas as interfaces (PC/App) para o Orb "pulsar" indicando aprendizado
        await manager.broadcast({
            "event": "learning_pulse", 
            "message": f"Assimilando dados de {url}..."
        })

    return {"status": "ok", "message": "Fragmento cognitivo sincronizado."}
