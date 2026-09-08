import os
import sys
from pathlib import Path

# Adiciona o diretório raiz do orchestrator no path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from memory.rag import memory_bank

SPELLBOOK_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "agent_blueprints")

def ingest_spellbook():
    print("🧙‍♂️ Iniciando a leitura do Livro de Magias (awesome-llm-apps)...")
    
    count = 0
    for root, dirs, files in os.walk(SPELLBOOK_DIR):
        for file in files:
            if file.endswith(('.md', '.py')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        if len(content) > 100:
                            # Adiciona no ChromaDB
                            memory_bank.memorize(
                                text=content,
                                metadata={"source": "awesome-llm-apps", "file": file, "path": filepath}
                            )
                            count += 1
                            print(f"📖 Aprendido: {file}")
                except Exception as e:
                    print(f"⚠️ Erro ao ler {file}: {e}")

    print(f"\n✅ {count} feitiços (arquivos) foram injetados no hipocampo do A.L.F.R.E.D.!")

if __name__ == "__main__":
    ingest_spellbook()
