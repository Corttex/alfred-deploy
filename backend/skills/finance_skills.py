import yfinance as yf

def get_stock_price(ticker: str) -> str:
    """
    Busca o preço atual e o resumo de uma ação, criptomoeda ou moeda.
    Exemplos de Tickers:
    - 'USDBRL=X' para cotação do Dólar em Real.
    - 'PETR4.SA' para Petrobras (B3).
    - 'BTC-USD' para Bitcoin.
    """
    try:
        asset = yf.Ticker(ticker)
        data = asset.fast_info
        last_price = data.last_price
        
        return f"Ativo: {ticker}\nPreço Atual: {last_price:.2f}"
    except Exception as e:
        return f"Erro ao buscar informações do ticker '{ticker}': {str(e)}"
