"""Base class para todos os agentes."""

from abc import ABC, abstractmethod
from models import Task, TaskResult


class BaseAgent(ABC):
    name: str = "base"

    @abstractmethod
    async def run(self, task: Task) -> TaskResult:
        pass
