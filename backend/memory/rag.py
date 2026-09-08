"""
Módulo de Memória RAG (Retrieval-Augmented Generation)
Usa ChromaDB local para armazenar e buscar contexto (memórias).
"""

import os
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from config import settings

# Diretório onde as memórias do ALFRED serão salvas fisicamente
PERSIST_DIRECTORY = os.path.join(os.path.dirname(__file__), "..", ".alfred_memory")

class AlfredMemory:
    def __init__(self):
        # Usaremos os Embeddings rápidos e baratos da OpenAI (text-embedding-3-small)
        self.embeddings = None
        self.vector_store = None
        
        if settings.OPENAI_API_KEY:
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small", 
                openai_api_key=settings.OPENAI_API_KEY
            )
            self.vector_store = Chroma(
                collection_name="alfred_long_term_memory",
                embedding_function=self.embeddings,
                persist_directory=PERSIST_DIRECTORY
            )

    def memorize(self, text: str, metadata: dict = None):
        """Salva uma nova informação na memória de longo prazo."""
        if not self.vector_store:
            return "Erro: Banco de memória não inicializado (Falta OPENAI_API_KEY)."
        
        metadata = metadata or {"source": "user_instruction"}
        self.vector_store.add_texts(texts=[text], metadatas=[metadata])
        return f"Memória armazenada com sucesso."

    def recall(self, query: str, k: int = 3) -> str:
        """Busca as memórias mais relevantes baseadas na semântica da pergunta."""
        if not self.vector_store:
            return ""
            
        docs = self.vector_store.similarity_search(query, k=k)
        if not docs:
            return ""
            
        context = "\n---\n".join([doc.page_content for doc in docs])
        return f"\n[Memórias Relevantes Recuperadas]:\n{context}\n"

# Instância global para ser usada pelos agentes
memory_bank = AlfredMemory()
