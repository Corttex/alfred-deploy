"""
Habilidades de Mídia (Media Skills)
Integra-se com a CLI da muapi.ai para geração autônoma de Imagens, Vídeos e Áudio.
"""
from .os_skills import os_execute_cli

def generate_media_cli(media_type: str, prompt: str, model: str = None) -> dict:
    """
    Gera mídia usando o muapi-cli nativamente no sistema operacional.
    """
    model_flag = f" --model {model}" if model else ""
    
    # Tratamento de aspas no prompt para evitar injeção ou quebra no CLI
    safe_prompt = prompt.replace('"', '\\"')
    cmd = f'muapi {media_type} generate --prompt "{safe_prompt}"{model_flag}'
    
    # Marca como critical=True pois consome créditos (API paga) ou muita CPU (Local Inference)
    return os_execute_cli(cmd, critical=True)
