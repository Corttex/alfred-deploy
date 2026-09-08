#!/usr/bin/env python3
"""
Script de inicializacao do A.L.F.R.E.D. Orchestrator.
Uso: python start.py
"""

import os
import sys

# Forca UTF-8 no Windows
os.environ["PYTHONUTF8"] = "1"

import uvicorn
from rich.console import Console
from rich.panel import Panel

console = Console(force_terminal=True, highlight=False)


def check_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    example_path = os.path.join(os.path.dirname(__file__), ".env.example")
    if not os.path.exists(env_path):
        import shutil
        shutil.copy(example_path, env_path)
        console.print("[yellow]AVISO: .env criado a partir de .env.example. Configure as chaves.[/yellow]")


def main():
    check_env()

    # Muda para o diretorio do script para imports funcionarem
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    console.print(Panel.fit(
        "[bold cyan]A.L.F.R.E.D.[/bold cyan]\n"
        "[dim]Autonomous Logic Framework for Remote Execution & Development[/dim]\n\n"
        "[green]>> Orquestrador iniciando...[/green]\n"
        "[dim]WebSocket : ws://localhost:8765/ws/[client_id]?token=...[/dim]\n"
        "[dim]REST      : http://localhost:8765/health[/dim]",
        border_style="cyan"
    ))

    from config import settings
    uvicorn.run(
        "main:app",
        host=settings.effective_host,
        port=settings.effective_port,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
