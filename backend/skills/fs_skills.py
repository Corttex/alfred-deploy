"""Skills de Sistema de Arquivos (File System)"""
import os
from .core import RequireApproval

def fs_write_file(path: str, content: str) -> dict:
    """Cria ou sobrescreve um arquivo no disco local."""
    # Como escrever arquivos pode sobrescrever código, poderíamos usar um HITL leve.
    # Mas para o DevAgent ter fluidez, vamos deixar aberto para pastas de projeto.
    try:
        abs_path = os.path.abspath(path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return {"status": "success", "message": f"Arquivo escrito com sucesso em: {abs_path}"}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao escrever {path}: {str(e)}"}
