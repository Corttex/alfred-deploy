"""Módulo core para Skills (Segurança HITL)."""

class RequireApproval(Exception):
    """Exceção levantada quando uma Skill requer aprovação humana (HITL)."""
    def __init__(self, action: str, details: str):
        self.action = action
        self.details = details
        super().__init__(f"HITL REQUIRED: {action} - {details}")
