import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .rag import memory_bank

class RAGSyncHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
            
        filepath = event.src_path
        if filepath.endswith(('.txt', '.md', '.py', '.js', '.ts')):
            print(f"[Watcher] Arquivo alterado: {filepath}. Sincronizando com o Hipocampo (RAG)...")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Sincroniza o conteúdo do arquivo com o RAG
                metadata = {"source": filepath, "type": "auto_sync"}
                memory_bank.memorize(f"Conteúdo atualizado do arquivo {filepath}:\n\n{content}", metadata=metadata)
                print(f"[Watcher] Arquivo {os.path.basename(filepath)} memorizado com sucesso.")
            except Exception as e:
                print(f"[Watcher] Erro ao ler/memorizar {filepath}: {e}")

def start_watcher(watch_dir: str):
    """Inicia o vigia em uma thread separada para não travar o servidor principal."""
    if not os.path.exists(watch_dir):
        print(f"[Watcher] Diretório {watch_dir} não existe. Ignorando sync automático.")
        return

    print(f"[Watcher] Iniciando Auto-Sync (Oikb) no diretório: {watch_dir}")
    event_handler = RAGSyncHandler()
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=True)
    
    def run_observer():
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    thread = threading.Thread(target=run_observer, daemon=True)
    thread.start()
