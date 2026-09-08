"""
MediaAgent — O Especialista em Produção Audiovisual
Gera e processa imagens, vídeos e áudio de forma autônoma usando muapi-cli.
"""
import anthropic
from config import settings
from models import Task, TaskResult, TaskStatus
from agents.base import BaseAgent
from skills.media_skills import generate_media_cli
from skills.core import RequireApproval

MEDIA_SYSTEM = """Você é o MediaAgent do A.L.F.R.E.D.
Sua especialidade é gerar Mídia (Imagens, Vídeos, Áudio, Animações) de forma autônoma.
Sempre traduza a intenção do usuário para prompts ALTAMENTE DETALHADOS EM INGLÊS antes de chamar a tool.

Exemplo de prompt: "A hyper-realistic cinematic shot of a cyborg working in a futuristic laboratory, neon lights, 8k resolution, photorealistic"
"""

TOOLS = [
    {
        "name": "generate_media_cli",
        "description": "Gera imagens, vídeos ou áudio através da CLI muapi.ai.",
        "input_schema": {
            "type": "object",
            "properties": {
                "media_type": {"type": "string", "enum": ["image", "video", "audio"], "description": "O tipo de mídia"},
                "prompt": {"type": "string", "description": "Prompt detalhado em inglês para a geração"},
                "model": {"type": "string", "description": "Opcional. Ex: flux-schnell, kling-video, sd.cpp (para rodar local sem custo)"}
            },
            "required": ["media_type", "prompt"]
        }
    }
]

class MediaAgent(BaseAgent):
    name = "media"

    async def run(self, task: Task) -> TaskResult:
        if not settings.ANTHROPIC_API_KEY:
            return TaskResult(task_id=task.id, status=TaskStatus.ERROR, output="Sem API Key.", agent_used=self.name)

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        messages = [{"role": "user", "content": task.command}]

        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=2048,
                system=MEDIA_SYSTEM,
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
                    
                    if tool_name == "generate_media_cli":
                        # Sempre define model=None caso a LLM não preencha
                        model_name = tool_args.get("model", None)
                        result_data = generate_media_cli(tool_args["media_type"], tool_args["prompt"], model_name)
                        
                        final_text += f"\n[🎨 Media Generated - {tool_args['media_type']}]\n"
                        if result_data.get('stdout'):
                            final_text += f"```bash\n{result_data['stdout'][:500]}\n```\n"
                        if result_data.get('error') or result_data.get('stderr'):
                            final_text += f"⚠️ Falha: {result_data.get('error') or result_data.get('stderr')}\n"
            
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.SUCCESS,
                output=final_text.strip() or "Processado com sucesso.",
                agent_used=self.name
            )

        except RequireApproval as e:
            raise e
        except Exception as e:
            return TaskResult(task_id=task.id, status=TaskStatus.ERROR, output=str(e), agent_used=self.name)
