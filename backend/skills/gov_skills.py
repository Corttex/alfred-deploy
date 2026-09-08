import httpx

def consult_cnpj(cnpj: str) -> str:
    """
    Consulta dados públicos de CNPJ diretamente na Receita Federal via BrasilAPI (proxy público do Gov.br).
    O CNPJ deve conter apenas números.
    """
    try:
        cnpj_clean = ''.join(filter(str.isdigit, cnpj))
        resp = httpx.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_clean}", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return f"Empresa: {data.get('razao_social')}\nFantasia: {data.get('nome_fantasia')}\nSituação: {data.get('descricao_situacao_cadastral')}\nCNAE: {data.get('cnae_fiscal_descricao')}"
        return f"Erro ao buscar CNPJ: {resp.text}"
    except Exception as e:
        return f"Erro na requisição: {str(e)}"

def consult_cep(cep: str) -> str:
    """
    Consulta endereço de um CEP nos Correios via BrasilAPI (Proxy do Gov.br).
    """
    try:
        cep_clean = ''.join(filter(str.isdigit, cep))
        resp = httpx.get(f"https://brasilapi.com.br/api/cep/v1/{cep_clean}", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return f"Endereço: {data.get('street')}, {data.get('neighborhood')} - {data.get('city')}/{data.get('state')}"
        return "CEP não encontrado."
    except Exception as e:
        return f"Erro na requisição: {str(e)}"
