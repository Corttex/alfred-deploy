"""Modelos de dados do orquestrador."""

from pydantic import BaseModel
from typing import Any


class Task(BaseModel):
    id: str
    command: str
    context: dict[str, Any] = {}
    client_id: str
    timestamp: str


class TaskResult(BaseModel):
    task_id: str
    status: str  # "success" | "error" | "partial"
    output: str
    agent_used: str
    metadata: dict[str, Any] = {}


class TaskStatus:
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    PENDING_APPROVAL = "pending_approval"
