from duckduckgo_search import DDGS
from .core import RequireApproval

def web_search(query: str, max_results: int = 5) -> str:
    """
    Pesquisa na internet usando o DuckDuckGo (sem necessidade de API Key).
    Retorna os links e resumos (snippets) dos resultados mais relevantes.
    Excelente para buscar notícias, documentações ou resolver bugs recentes.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            
            if not results:
                return "Nenhum resultado encontrado para a pesquisa."
            
            output = f"Resultados da Pesquisa na Web para: '{query}'\n\n"
            for idx, r in enumerate(results, 1):
                output += f"{idx}. {r.get('title', 'Sem Título')}\n"
                output += f"   Link: {r.get('href', 'Sem URL')}\n"
                output += f"   Resumo: {r.get('body', 'Sem resumo disponível')}\n\n"
                
            return output
    except Exception as e:
        return f"Erro ao realizar pesquisa na internet: {str(e)}"
