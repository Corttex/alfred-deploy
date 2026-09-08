"""
MonitorAgent — Monitora a saúde do sistema local e das VPS via Telemetria.
"""
import anthropic
from config import settings
from models import Task, TaskResult, TaskStatus
from agents.base import BaseAgent
from skills.os_skills import os_execute_cli
from skills.coolify_skills import coolify_api_request
from memory.rag import memory_bank
from skills.core import RequireApproval

MONITOR_SYSTEM = """Você é o MonitorAgent do A.L.F.R.E.D.
Sua função é vigiar e reportar o uso de recursos (CPU, RAM, Disco, rede) e saúde dos containers (Docker).

Você possui ferramentas para diagnóstico:
1. `ssh_execute`: Para vigiar servidores remotos (VPS).
2. `os_execute_cli`: Para vigiar a máquina host (Localhost).
3. `coolify_api_request`: Para listar aplicações e ver status (via endpoint /api/v1/applications).

Utilize comandos Linux padrão de diagnóstico (`top -bn1`, `free -h`, `df -h`, `docker ps`) no SSH, ou bata na API do Coolify.
Por padrão, defina critical=False para comandos investigativos. Só use critical=True se decidir matar processos (kill) para recuperar a saúde do sistema."""

TOOLS = [
    {
        "name": "ssh_execute",
        "description": "Executa telemetria em VPS Remota.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "critical": {"type": "boolean"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "os_execute_cli",
        "description": "Executa telemetria na máquina Local.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "critical": {"type": "boolean"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "coolify_api_request",
        "description": "Faz chamadas REST para a API do Coolify para verificar status dos apps.",
        "input_schema": {
            "type": "object",
            "properties": {
                "endpoint": {"type": "string"},
                "method": {"type": "string"},
                "payload": {"type": "object"},
                "critical": {"type": "boolean"}
            },
            "required": ["endpoint"]
        }
    }
]

class MonitorAgent(BaseAgent):
    name = "monitor"

    async def run(self, task: Task) -> TaskResult:
        if not settings.ANTHROPIC_API_KEY:
            return TaskResult(task_id=task.id, status=TaskStatus.ERROR, output="ANTHROPIC_API_KEY não configurada.", agent_used=self.name)

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        
        past_context = ""
        try:
            past_context = memory_bank.recall(task.command)
        except Exception:
            pass
            
        enriched_prompt = f"{past_context}\n\n[Nova Instrução]: {task.command}" if past_context else task.command

        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=4096,
                system=MONITOR_SYSTEM,
                messages=[{"role": "user", "content": enriched_prompt}],
                tools=TOOLS
            )

            final_text = ""
            for block in response.content:
                if block.type == "text":
                    final_text += block.text + "\n"
                elif block.type == "tool_use":
                    tool_name = block.name
                    tool_args = block.input
                    
                    if tool_name == "ssh_execute":
                        result = ssh_execute(**tool_args)
                        final_text += f"\n[📡 Remoto] `{tool_args['command']}`\n```bash\n{result.get('stdout', '')[:1000]}\n```\n"
                    elif tool_name == "os_execute_cli":
                        result = os_execute_cli(**tool_args)
                        final_text += f"\n[💻 Local] `{tool_args['command']}`\n```bash\n{result.get('stdout', '')[:1000]}\n```\n"
                    elif tool_name == "coolify_api_request":
                        result = coolify_api_request(**tool_args)
                        final_text += f"\n[☁️ Coolify API] `{tool_args.get('method', 'GET')} {tool_args['endpoint']}`\n```json\n{str(result.get('data', result.get('error')))[:1000]}\n```\n"
            
            return TaskResult(task_id=task.id, status=TaskStatus.SUCCESS, output=final_text.strip() or "Telemetria silenciosa executada.", agent_used=self.name)
        except RequireApproval as e:
            raise e
        except Exception as e:
            return TaskResult(task_id=task.id, status=TaskStatus.ERROR, output=f"Falha de Monitoramento: {str(e)}", agent_used=self.name)
