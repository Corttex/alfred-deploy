"""
DeployAgent — Executa deploys na VPS via SSH.
Conecta via Paramiko e executa os comandos do workflow de deploy.
"""

import anthropic
import os
from config import settings
from models import Task, TaskResult, TaskStatus
from agents.base import BaseAgent
from skills.ssh_skills import ssh_execute
from skills.coolify_skills import coolify_api_request
from skills.core import RequireApproval
from memory.rag import memory_bank

DEPLOY_SYSTEM = """Você é o DeployAgent (SysAdmin) do A.L.F.R.E.D.
Sua especialidade é gerenciar infraestrutura em nuvem e servidores Linux.

IMPORTANTE: A infraestrutura do usuário é gerenciada pelo **Coolify**.
Diretrizes:
- Você possui acesso à API do Coolify via ferramenta `coolify_api_request`.
- Sempre que possível, utilize a API do Coolify para listar projetos (`/api/v1/applications`), forçar deploys ou ver status, em vez de acessar via SSH bruto.
- Para analisar erros profundos que a API não exibe, logue via SSH (`ssh_execute`) e use `docker ps` e `docker logs`.
- DICA IMPORTANTE: Ao rodar SSH, as sessões não mantêm estado entre chamadas. Encadeie com `&&`.

Sempre que a ação modificar o estado do servidor ou realizar deploys, defina critical=True. Para leitura (logs, ls, get na API), critical=False."""

TOOLS = [
    {
        "name": "ssh_execute",
        "description": "Executa comandos bash em uma VPS remota via SSH.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Comando bash a executar no servidor remoto"},
                "critical": {"type": "boolean"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "coolify_api_request",
        "description": "Faz chamadas para a API REST do Coolify (para listar apps, iniciar deploy, etc).",
        "input_schema": {
            "type": "object",
            "properties": {
                "endpoint": {"type": "string", "description": "Endpoint da API (ex: /api/v1/applications)"},
                "method": {"type": "string", "description": "GET, POST, PUT, DELETE (padrão GET)"},
                "payload": {"type": "object", "description": "Corpo JSON (opcional)"},
                "critical": {"type": "boolean", "description": "True se for POST/PUT/DELETE que altera estado."}
            },
            "required": ["endpoint"]
        }
    }
]

class DeployAgent(BaseAgent):
    name = "deploy"

    async def run(self, task: Task) -> TaskResult:
        if not settings.ANTHROPIC_API_KEY:
            return TaskResult(
                task_id=task.id, status=TaskStatus.ERROR,
                output="ANTHROPIC_API_KEY não configurada no .env", agent_used=self.name
            )
            
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        
        # --- RAG: Resgate de Memória ---
        past_context = ""
        try:
            past_context = memory_bank.recall(task.command)
        except Exception:
            pass
            
        enriched_prompt = f"{past_context}\n\n[Nova Instrução]: {task.command}" if past_context else task.command
        
        messages = [{"role": "user", "content": enriched_prompt}]

        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=4096,
                system=DEPLOY_SYSTEM,
                messages=messages,
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
                        result_data = ssh_execute(**tool_args)
                        final_text += f"\n[🌐 SSH Executed] `{tool_args['command']}`\n"
                        if result_data.get('stdout'):
                            final_text += f"```bash\n{result_data['stdout'][:800]}\n```\n"
                        if result_data.get('stderr'):
                            final_text += f"Erros:\n```bash\n{result_data['stderr'][:800]}\n```\n"
                        if result_data.get('error'):
                            final_text += f"⚠️ Falha de Conexão: {result_data['error']}\n"
                    
                    elif tool_name == "coolify_api_request":
                        result_data = coolify_api_request(**tool_args)
                        final_text += f"\n[☁️ Coolify API] `{tool_args.get('method', 'GET')} {tool_args['endpoint']}`\n"
                        if result_data.get('data'):
                            # Stringify JSON response safely without importing json inside run
                            final_text += f"```json\n{str(result_data['data'])[:1000]}\n```\n"
                        if result_data.get('error'):
                            final_text += f"⚠️ Erro: {result_data['error']}\nDetalhes: {result_data.get('details', '')}\n"
            
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.SUCCESS,
                output=final_text.strip() or "Processado sem execução explícita.",
                agent_used=self.name,
            )

        except RequireApproval as e:
            raise e
        except Exception as e:
            return TaskResult(
                task_id=task.id, status=TaskStatus.ERROR,
                output=f"Falha de execução SysAdmin: {str(e)}", agent_used=self.name
            )
