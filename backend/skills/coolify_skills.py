"""
Skills de integração com a API REST do Coolify.
Permite iniciar deploys, ler logs e consultar projetos.
"""
import urllib.request
import urllib.error
import json
from config import settings
from .core import RequireApproval

def coolify_api_request(endpoint: str, method: str = "GET", payload: dict = None, critical: bool = False) -> dict:
    """Faz uma requisição HTTP nativa para a API REST do Coolify."""
    
    if critical:
        raise RequireApproval(
            action="coolify_api_request",
            details=f"Ação destrutiva ou mutável via API Coolify: {method} {endpoint}"
        )
        
    base_url = getattr(settings, "COOLIFY_API_URL", "").rstrip("/")
    token = getattr(settings, "COOLIFY_API_TOKEN", "")
    
    if not base_url or not token:
        return {"error": "COOLIFY_API_URL ou COOLIFY_API_TOKEN não estão configurados no arquivo .env."}
        
    url = f"{base_url}{endpoint if endpoint.startswith('/') else '/' + endpoint}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    data = None
    if payload:
        data = json.dumps(payload).encode("utf-8")
        
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            try:
                return {"status": response.status, "data": json.loads(res_body)}
            except json.JSONDecodeError:
                return {"status": response.status, "data": res_body}
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8')
        return {"error": f"Erro HTTP {e.code}", "details": err_msg}
    except Exception as e:
        return {"error": f"Falha de conexão com a API Coolify: {str(e)}"}
