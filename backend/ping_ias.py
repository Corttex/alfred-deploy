import os
import time
import requests
from dotenv import load_dotenv

# Carrega as chaves do .env
load_dotenv(".env")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("Iniciando PING em 15 IAs...\n")

# Lista de modelos e suas respectivas APIs
models_to_test = [
    # --- ANTHROPIC (Direct API) ---
    {"name": "Claude 3.5 Sonnet (Anthropic API)", "url": "https://api.anthropic.com/v1/messages", "headers": {"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"}, "payload": {"model": "claude-3-5-sonnet-20240620", "max_tokens": 10, "messages": [{"role": "user", "content": "Diga 'Pong' e nada mais."}]}},
    
    # --- GOOGLE (Direct API via REST) ---
    {"name": "Gemini 2.5 Pro (Google API)", "url": f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={GOOGLE_API_KEY}", "headers": {"Content-Type": "application/json"}, "payload": {"contents": [{"parts": [{"text": "Diga 'Pong' e nada mais."}]}]}},
    {"name": "Gemini 2.5 Flash (Google API)", "url": f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GOOGLE_API_KEY}", "headers": {"Content-Type": "application/json"}, "payload": {"contents": [{"parts": [{"text": "Diga 'Pong' e nada mais."}]}]}},

    # --- GROQ (OpenAI Compatible) ---
    {"name": "GPT-OSS 120B (Groq)", "url": "https://api.groq.com/openai/v1/chat/completions", "headers": {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}, "payload": {"model": "openai/gpt-oss-120b", "messages": [{"role": "user", "content": "Diga 'Pong' e nada mais."}]}},
    {"name": "Qwen 3.8 27B (Groq)", "url": "https://api.groq.com/openai/v1/chat/completions", "headers": {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}, "payload": {"model": "qwen/qwen3.8-27b", "messages": [{"role": "user", "content": "Diga 'Pong' e nada mais."}]}},
    {"name": "Groq Compound (Groq)", "url": "https://api.groq.com/openai/v1/chat/completions", "headers": {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}, "payload": {"model": "groq/compound", "messages": [{"role": "user", "content": "Diga 'Pong' e nada mais."}]}},
    
    # --- OPENROUTER (Multi-Models) ---
    {"name": "GPT-4o (OpenRouter)", "url": "https://openrouter.ai/api/v1/chat/completions", "headers": {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}, "payload": {"model": "openai/gpt-4o", "messages": [{"role": "user", "content": "Diga 'Pong' e nada mais."}]}},
    {"name": "GPT-4o-Mini (OpenRouter)", "url": "https://openrouter.ai/api/v1/chat/completions", "headers": {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}, "payload": {"model": "openai/gpt-4o-mini", "messages": [{"role": "user", "content": "Diga 'Pong' e nada mais."}]}},
    {"name": "Claude 3 Haiku (OpenRouter)", "url": "https://openrouter.ai/api/v1/chat/completions", "headers": {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}, "payload": {"model": "anthropic/claude-3-haiku", "messages": [{"role": "user", "content": "Diga 'Pong' e nada mais."}]}},
    {"name": "Meta Llama 3.1 405B (OpenRouter)", "url": "https://openrouter.ai/api/v1/chat/completions", "headers": {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}, "payload": {"model": "meta-llama/llama-3.1-405b-instruct", "messages": [{"role": "user", "content": "Diga 'Pong' e nada mais."}]}},
    {"name": "Qwen 2.5 72B (OpenRouter)", "url": "https://openrouter.ai/api/v1/chat/completions", "headers": {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}, "payload": {"model": "qwen/qwen-2.5-72b-instruct", "messages": [{"role": "user", "content": "Diga 'Pong' e nada mais."}]}},
    {"name": "Mistral Large (OpenRouter)", "url": "https://openrouter.ai/api/v1/chat/completions", "headers": {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}, "payload": {"model": "mistralai/mistral-large", "messages": [{"role": "user", "content": "Diga 'Pong' e nada mais."}]}},
    {"name": "Google Gemma 2 27B (OpenRouter)", "url": "https://openrouter.ai/api/v1/chat/completions", "headers": {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}, "payload": {"model": "google/gemma-2-27b-it", "messages": [{"role": "user", "content": "Diga 'Pong' e nada mais."}]}},
    {"name": "Cohere Command R+ (OpenRouter)", "url": "https://openrouter.ai/api/v1/chat/completions", "headers": {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}, "payload": {"model": "cohere/command-r-plus", "messages": [{"role": "user", "content": "Diga 'Pong' e nada mais."}]}},
    {"name": "Nous Hermes 2 Mixtral (OpenRouter)", "url": "https://openrouter.ai/api/v1/chat/completions", "headers": {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}, "payload": {"model": "nousresearch/nous-hermes-2-mixtral-8x7b-dpo", "messages": [{"role": "user", "content": "Diga 'Pong' e nada mais."}]}}
]

for i, model in enumerate(models_to_test):
    print(f"[{i+1}/15] Pingando {model['name']}...")
    start_time = time.time()
    try:
        response = requests.post(model['url'], headers=model['headers'], json=model['payload'], timeout=10)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            latency = round((end_time - start_time) * 1000)
            
            # Extrair a resposta com base na API
            if "anthropic" in model['name'].lower():
                reply = data['content'][0]['text']
            elif "google" in model['name'].lower() and not "openrouter" in model['name'].lower():
                reply = data['candidates'][0]['content']['parts'][0]['text']
            else: # OpenAI / OpenRouter / Groq format
                reply = data['choices'][0]['message']['content']
                
            print(f"  [SUCESSO] Tempo: {latency}ms | Resposta: {reply.strip()}")
        else:
            print(f"  [ERRO] HTTP {response.status_code} - {response.text[:100]}...")
    except Exception as e:
         print(f"  [FALHA] Não foi possível conectar: {str(e)}")
    print("-" * 40)

print("\nTeste concluído!")
