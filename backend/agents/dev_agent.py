"""
DevAgent — Geração de código e boilerplates.
Usa o LLM com contexto dos padrões do Felipe para gerar código.
"""

import anthropic
import json
from config import settings
from models import Task, TaskResult, TaskStatus
from agents.base import BaseAgent
from skills.os_skills import os_execute_cli
from skills.fs_skills import fs_write_file
from skills.web_skills import web_search
from skills.core import RequireApproval
from memory.rag import memory_bank

DEV_SYSTEM = """Você é o DevAgent do A.L.F.R.E.D., engenheiro chefe de Felipe Azevedo.

Diretrizes:
- Frontend: Next.js App Router + Vanilla CSS (Liquid Glass UI)
- Backend: FastAPI (Python) ou Next.js API Routes
- Banco: Supabase
- Deploy: Docker
- Padrões: Código limpo, tipado, modular.

Você tem autonomia! Sempre que pedirem para criar um projeto ou arquivo, USE SUAS FERRAMENTAS para escrever no disco ou rodar comandos (ex: npx, npm install). Não responda apenas com código Markdown se puder escrevê-lo diretamente.
Se for rodar um comando perigoso, defina critical=True."""

TOOLS = [
    {
        "name": "os_execute_cli",
        "description": "Executa um comando no terminal do sistema.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Comando CLI (ex: npm i, mkdir, npx create-next-app)"},
                "cwd": {"type": "string", "description": "Diretório de execução (opcional)"},
                "critical": {"type": "boolean", "description": "True se for um comando perigoso/destrutivo"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "fs_write_file",
        "description": "Cria ou sobrescreve um arquivo no disco.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Caminho do arquivo (ex: ./src/app/page.tsx)"},
                "content": {"type": "string", "description": "Conteúdo completo do arquivo"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "web_search",
        "description": "Realiza uma pesquisa na internet (DuckDuckGo) para buscar documentações, erros ou informações atualizadas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "A frase exata para pesquisar no buscador."},
                "max_results": {"type": "integer", "description": "Quantidade máxima de resultados (padrão 5)"}
            },
            "required": ["query"]
        }
    }
]


class DevAgent(BaseAgent):
    name = "dev"

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
            pass # Ignora erro de memória para não travar o fluxo
            
        enriched_prompt = f"{past_context}\n\n[Nova Instrução]: {task.command}" if past_context else task.command
        
        messages = [{"role": "user", "content": enriched_prompt}]

        try:
            # 1. Primeira chamada à LLM (Pensamento e Decisão de Tool)
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=4096,
                system=DEV_SYSTEM,
                messages=messages,
                tools=TOOLS
            )

            final_text = ""
            for block in response.content:
                if block.type == "text":
                    final_text += block.text + "\n"
                
                # 2. Execução da Ferramenta (Se a LLM decidir usar uma)
                elif block.type == "tool_use":
                    tool_name = block.name
                    tool_args = block.input
                    
                    if tool_name == "os_execute_cli":
                        # Se crítico, levantará RequireApproval que será pego pelo Router
                        result_data = os_execute_cli(**tool_args)
                        final_text += f"\n[⚙️ CLI] Executei: `{tool_args['command']}`\n"
                    
                    elif tool_name == "fs_write_file":
                        result_data = fs_write_file(**tool_args)
                        final_text += f"\n[💾 Arquivo Salvo] {tool_args['path']}\n"
                    
                    elif tool_name == "web_search":
                        result_data = web_search(**tool_args)
                        final_text += f"\n[🌐 Pesquisa Web] Busquei por: '{tool_args['query']}'\n"
                        final_text += f"\n```\n{result_data}\n```\n"
            
            # (Num sistema maduro, devolveríamos o result_data para a LLM, mas para MVP vamos reportar direto)
            
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.SUCCESS,
                output=final_text.strip() or "Tarefa executada silenciosamente.",
                agent_used=self.name,
            )

        except RequireApproval as e:
            # Repassa a exceção de Segurança para o Orquestrador parar o fluxo
            raise e
        except Exception as e:
            return TaskResult(
                task_id=task.id, status=TaskStatus.ERROR,
                output=f"Falha de execução do Claude: {str(e)}", agent_used=self.name
            )
