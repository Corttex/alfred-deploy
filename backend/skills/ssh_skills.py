"""Skills de Comunicação SSH Remota (VPS)"""
import os
import paramiko
from config import settings
from .core import RequireApproval

def ssh_execute(command: str, host: str = None, user: str = None, key_path: str = None, critical: bool = False) -> dict:
    """Executa um comando remoto via SSH na VPS."""
    
    if critical:
        raise RequireApproval(
            action="ssh_execute",
            details=f"Comando remoto perigoso/mutável na VPS: '{command}'"
        )
        
    host = host or settings.VPS_01_HOST
    user = user or settings.VPS_01_USER
    key_path = key_path or settings.VPS_01_SSH_KEY_PATH
    
    if not host:
        return {"error": "Servidor de destino (HOST) não configurado."}
        
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        expanded_key_path = os.path.expanduser(key_path)
        client.connect(
            hostname=host,
            username=user,
            key_filename=expanded_key_path,
            timeout=15,
        )
        
        _, stdout, stderr = client.exec_command(command)
        out = stdout.read().decode('utf-8').strip()
        err = stderr.read().decode('utf-8').strip()
        
        client.close()
        
        return {
            "stdout": out,
            "stderr": err
        }
    except Exception as e:
        return {"error": f"Falha de conexão SSH: {str(e)}"}
