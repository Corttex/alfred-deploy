import os
import logging

def create_project_folder(project_name: str) -> str:
    """
    Cria uma nova pasta de projeto no diretório pai do ALFRED.
    """
    # Acessa a Área de Trabalho (diretório pai do BK/Apps)
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    project_path = os.path.join(base_path, project_name)
    
    try:
        os.makedirs(project_path, exist_ok=True)
        logging.info(f"[DEV AGENT] Pasta '{project_name}' criada em: {project_path}")
        return f"Sucesso! A pasta do projeto '{project_name}' foi criada em {project_path}"
    except Exception as e:
        return f"Erro ao criar pasta: {str(e)}"

def write_code_file(path: str, code: str) -> str:
    """
    Escreve código dentro de um arquivo no sistema local.
    """
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        return f"Arquivo '{path}' gerado com sucesso."
    except Exception as e:
        return f"Erro ao gerar arquivo: {str(e)}"
