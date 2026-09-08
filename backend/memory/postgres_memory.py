import os
import logging
from dotenv import load_dotenv
from langchain_postgres import PostgresChatMessageHistory
import psycopg

load_dotenv()

def get_session_history(session_id: str):
    """
    Recupera ou cria o histórico de conversa unificado no PostgreSQL.
    Todas as telas (Web, Mobile, Extensão) que chamarem essa função com o mesmo session_id
    verão o mesmíssimo histórico de pensamento do ALFRED.
    """
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        logging.warning("DATABASE_URL não configurada. A Memória não vai funcionar!")
        return None
        
    table_name = "alfred_chat_history"
    
    # Estabelece conexão síncrona usando psycopg (versão 3)
    conn = psycopg.connect(db_url)
    
    # Inicia a tabela na nuvem do Coolify, vinculada ao session_id
    history = PostgresChatMessageHistory(
        table_name=table_name,
        session_id=session_id,
        sync_connection=conn
    )
    
    # Note: Para produção síncrona real, a classe PostgresChatMessageHistory requer `sync_connection`.
    return history
