"""
TaskRouter — Roteador inteligente usando o Córtex Frontal (LLM).
Substituiu o antigo roteamento por Regex.
"""

from models import Task, TaskResult, TaskStatus
from supervisor import AlfredSupervisor

class TaskRouter:
    def __init__(self):
        # Inicia a Mente de Colmeia
        self.supervisor = AlfredSupervisor()

    async def execute(self, task: Task) -> TaskResult:
        try:
            # Chama o LangChain + Groq + Agentes
            output = self.supervisor.process(task.command)
            
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.COMPLETED,
                output=output,
                agent_used="supervisor_llm"
            )
        except Exception as e:
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.ERROR,
                output=f"Erro crítico no Córtex: {str(e)}",
                agent_used="system",
            )
