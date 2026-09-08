import os
from tavily import TavilyClient
import logging
from dotenv import load_dotenv

load_dotenv()

def search_web(query: str) -> str:
    """
    Função engatilhada pelo botão 'Pesquisa Web'.
    Usa o Tavily para pesquisar na internet em tempo real e trazer resumos mastigados.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Erro: TAVILY_API_KEY não configurada no .env."

    logging.info(f"[WEB AGENT] Pesquisando na internet: '{query}'")
    
    try:
        client = TavilyClient(api_key=api_key)
        # Search the web and return the summarized context
        response = client.search(query, search_depth="advanced", max_results=3)
        
        # Formata o resultado
        results = []
        for res in response.get('results', []):
            results.append(f"Título: {res['title']}\nURL: {res['url']}\nConteúdo: {res['content']}\n")
            
        final_output = "\n---\n".join(results)
        return final_output if final_output else "Nenhum resultado encontrado."

    except Exception as e:
        return f"Falha crítica na Pesquisa Web: {str(e)}"
