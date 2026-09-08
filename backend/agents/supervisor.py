"""
SupervisorAgent — O Cérebro Mestre (Baseado no conceito de LangGraph).
Recebe tarefas complexas, quebra em sub-tarefas e coordena a equipe de Agentes (Dev, Git, Deploy, Monitor).
"""
import anthropic
import json
from config import settings
from models import Task, TaskResult, TaskStatus
from agents.base import BaseAgent
from agents.dev_agent import DevAgent
from agents.deploy_agent import DeployAgent
from agents.git_agent import GitAgent
from agents.media_agent import MediaAgent
from skills.core import RequireApproval

# Registramos os agentes subalternos
TEAM = {
    "dev": DevAgent(),
    "deploy": DeployAgent(),
    "git": GitAgent(),
    "media": MediaAgent()
}

SUPERVISOR_SYSTEM = """Você é o Agente Supervisor do A.L.F.R.E.D.
Sua função é analisar o pedido do usuário e determinar se ele requer a execução de múltiplos agentes em sequência.

Os agentes disponíveis na sua equipe são:
1. `dev`: Escreve código e cria arquivos no sistema.
2. `git`: Roda comandos git locais (commit, push).
3. `deploy`: Gerencia a VPS remota e a API do Coolify (para produção).
4. `media`: Gera imagens, vídeos e áudio usando IA.

Se a tarefa for simples e pertencer a um só agente, chame apenas ele.
Se for complexa (ex: "Crie um arquivo e depois faça o commit e deploy"), crie um plano ordenado.

Retorne EXCLUSIVAMENTE um JSON com o plano de ação no formato:
{
    "plan": [
        {"agent": "dev", "instruction": "Crie o arquivo x com conteúdo y"},
        {"agent": "git", "instruction": "Adicione x e faça commit"},
        {"agent": "deploy", "instruction": "Dê deploy na aplicação via Coolify"}
    ]
}"""

class SupervisorAgent(BaseAgent):
    name = "supervisor"

    async def run(self, task: Task) -> TaskResult:
        if not settings.ANTHROPIC_API_KEY:
            return TaskResult(task_id=task.id, status=TaskStatus.ERROR, output="Sem API Key.", agent_used=self.name)

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        try:
            # 1. O Supervisor pensa e cria o Plano de Execução (Roteamento Inteligente)
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=2048,
                system=SUPERVISOR_SYSTEM,
                messages=[{"role": "user", "content": task.command}],
                temperature=0.0
            )

            plan_text = response.content[0].text
            
            try:
                plan_json = json.loads(plan_text)
                steps = plan_json.get("plan", [])
            except json.JSONDecodeError:
                return TaskResult(task_id=task.id, status=TaskStatus.ERROR, output=f"Falha do Supervisor ao criar o plano:\n{plan_text}", agent_used=self.name)

            if not steps:
                return TaskResult(task_id=task.id, status=TaskStatus.SUCCESS, output="Nenhuma ação necessária.", agent_used=self.name)

            overall_output = "**[PLANO DO SUPERVISOR ESTABELECIDO]**\n"
            
            # 2. Executa a delegação em cascata
            for step in steps:
                agent_name = step.get("agent")
                instruction = step.get("instruction")
                
                if agent_name in TEAM:
                    overall_output += f"\n🔄 **Delegando para {agent_name.upper()}**: {instruction}...\n"
                    
                    # Cria uma subtarefa invisível para o agente subordinado
                    sub_task = Task(id=f"{task.id}-{agent_name}", command=instruction, context=task.context)
                    
                    try:
                        # Executa o subordinado
                        sub_result = await TEAM[agent_name].run(sub_task)
                        overall_output += f"✅ **{agent_name.upper()} concluiu**: {sub_result.output}\n"
                    except RequireApproval as e:
                        # Se qualquer subordinado esbarrar na segurança HITL, o Supervisor pausa tudo e repassa o bloqueio pra cima
                        raise RequireApproval(
                            action=e.action,
                            details=f"[Delegação de {agent_name.upper()}] {e.details}"
                        )
                    except Exception as e:
                        overall_output += f"❌ **Falha em {agent_name.upper()}**: {str(e)}\n"
                        # Interrompe a cadeia se um falhar
                        break
                else:
                    overall_output += f"⚠️ Agente desconhecido ignorado: {agent_name}\n"

            return TaskResult(
                task_id=task.id,
                status=TaskStatus.SUCCESS,
                output=overall_output.strip(),
                agent_used=self.name
            )

        except RequireApproval as e:
            raise e
        except Exception as e:
            return TaskResult(task_id=task.id, status=TaskStatus.ERROR, output=f"Erro Crítico do Supervisor: {str(e)}", agent_used=self.name)
