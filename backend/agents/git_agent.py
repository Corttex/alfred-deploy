"""
GitAgent — Gerencia repositórios locais e versionamento de código.
"""
import anthropic
from config import settings
from models import Task, TaskResult, TaskStatus
from agents.base import BaseAgent
from skills.os_skills import os_execute_cli
from skills.core import RequireApproval
from memory.rag import memory_bank

GIT_SYSTEM = """Você é o GitAgent do A.L.F.R.E.D.
Sua função é gerenciar o versionamento de código (Git/GitHub).

Você pode executar comandos git no sistema local usando a ferramenta `os_execute_cli`.
Exemplos: `git status`, `git diff`, `git add .`, `git commit -m "..."`, `git push`.

Sempre que a ação for destrutiva ou alterar o estado do repositório (ex: commit, push, reset --hard, merge), defina critical=True. Para ações apenas de leitura (status, log, diff), defina critical=False."""

TOOLS = [
    {
        "name": "os_execute_cli",
        "description": "Executa comandos no terminal local. Use para operações de git.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Comando CLI (ex: git status, git push)"},
                "cwd": {"type": "string", "description": "Diretório de trabalho do repositório (opcional)"},
                "critical": {"type": "boolean", "description": "True para comandos que alteram histórico ou sincronizam remote (push, commit, pull)."}
            },
            "required": ["command"]
        }
    }
]

class GitAgent(BaseAgent):
    name = "git"

    async def run(self, task: Task) -> TaskResult:
        if not settings.ANTHROPIC_API_KEY:
            return TaskResult(
                task_id=task.id, status=TaskStatus.ERROR,
                output="ANTHROPIC_API_KEY não configurada.", agent_used=self.name
            )

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
                system=GIT_SYSTEM,
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
                    
                    if tool_name == "os_execute_cli":
                        result = os_execute_cli(**tool_args)
                        final_text += f"\n[🐙 Git Local] Executado: `{tool_args['command']}`\n"
                        if result.get('stdout'): final_text += f"```bash\n{result['stdout'][:1000]}\n```\n"
                        if result.get('stderr'): final_text += f"```bash\n{result['stderr'][:1000]}\n```\n"
            
            return TaskResult(task_id=task.id, status=TaskStatus.SUCCESS, output=final_text.strip() or "Processado sem saída.", agent_used=self.name)
        except RequireApproval as e:
            raise e
        except Exception as e:
            return TaskResult(task_id=task.id, status=TaskStatus.ERROR, output=f"Falha no GitAgent: {str(e)}", agent_used=self.name)
