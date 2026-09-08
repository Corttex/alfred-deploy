"""
LLMAgent — Agente de fallback e Conhecimento Geral.
Responsável por conversas, respostas a dúvidas e por GERENCIAR a memória de longo prazo (RAG).
"""

import anthropic
import os
from config import settings
from models import Task, TaskResult, TaskStatus
from agents.base import BaseAgent
from memory.rag import memory_bank

KB_PATH = os.path.join(os.path.dirname(__file__), "../../knowledge_base")


def _load_knowledge_base() -> str:
    docs = []
    for fname in ["patterns.md", "workflows.md", "infrastructure.md", "llm_registry.md"]:
        fpath = os.path.join(KB_PATH, fname)
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                docs.append(f"### {fname}\n{f.read()}")
    return "\n\n".join(docs)


SYSTEM_PROMPT = f"""Você é A.L.F.R.E.D., o núcleo de IA principal de Felipe Azevedo.
Sua função aqui é conversar, esclarecer dúvidas e gerenciar as Memórias de Longo Prazo do sistema.

Se o usuário pedir para "lembrar", "guardar" ou "aprender" alguma configuração, regra ou dado importante, USE a ferramenta `save_to_memory` para persistir isso no banco vetorial.
Se o usuário fizer uma pergunta, responda de forma técnica e direta baseada no contexto.

=== BASE DE CONHECIMENTO ESTÁTICA ===
{_load_knowledge_base()}
===========================
"""

TOOLS = [
    {
        "name": "save_to_memory",
        "description": "Salva uma informação importante no banco de memória vetorial permanente do ALFRED.",
        "input_schema": {
            "type": "object",
            "properties": {
                "fact": {"type": "string", "description": "A regra, dado, ou fato claro que deve ser memorizado"}
            },
            "required": ["fact"]
        }
    }
]


class LLMAgent(BaseAgent):
    name = "llm"

    async def run(self, task: Task) -> TaskResult:
        if not settings.ANTHROPIC_API_KEY:
            return TaskResult(
                task_id=task.id, status=TaskStatus.ERROR,
                output="ANTHROPIC_API_KEY não configurada no .env", agent_used=self.name
            )

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        
        # Faz recall de memórias passadas caso a pergunta do usuário precise
        past_context = ""
        try:
            past_context = memory_bank.recall(task.command)
        except Exception:
            pass
            
        enriched_prompt = f"[Memórias Resgatadas do Banco Vetorial]:\n{past_context}\n\n[Mensagem do Usuário]: {task.command}" if past_context else task.command

        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=2048,
                system=SYSTEM_PROMPT,
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
                    
                    if tool_name == "save_to_memory":
                        try:
                            memory_bank.memorize(tool_args["fact"], metadata={"source": "llm_agent"})
                            final_text += f"\n[🧠 Memória Atualizada] Guardei este fato com sucesso: `{tool_args['fact']}`\n"
                        except Exception as e:
                            final_text += f"\n[❌ Erro ao Memorizar]: {str(e)}\n"
            
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.SUCCESS,
                output=final_text.strip() or "Entendido.",
                agent_used=self.name,
            )
        except Exception as e:
            return TaskResult(
                task_id=task.id, status=TaskStatus.ERROR,
                output=f"Falha de processamento: {str(e)}", agent_used=self.name
            )
