"""Skills do Sistema Operacional (CLI, FS)"""
import subprocess
from .core import RequireApproval

def os_execute_cli(command: str, cwd: str = None, critical: bool = False):
    """
    Executa um comando no terminal local.
    Se 'critical=True', levanta RequireApproval para que o Roteador exija consentimento.
    """
    if critical:
        raise RequireApproval(
            action="os_execute_cli",
            details=f"Tentativa de executar comando crítico: '{command}'"
        )
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {"error": str(e)}
