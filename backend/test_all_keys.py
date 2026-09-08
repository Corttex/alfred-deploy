import os
import requests
import socket
from dotenv import load_dotenv

# Carrega as chaves
load_dotenv(".env")

def print_result(name, success, message=""):
    status = "✅ SUCESSO" if success else "❌ ERRO"
    print(f"{status} | {name}" + (f" -> {message}" if message else ""))

print("🚀 INICIANDO TESTE COMPLETO DE TODAS AS CHAVES E SERVIÇOS 🚀\n")

# ==========================================
# 1. LLMs (Adicionais ao ping_ias.py)
# ==========================================
print("--- 🧠 Modelos de IA ---")

# OpenAI
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key:
    try:
        r = requests.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {openai_key}"}, timeout=5)
        print_result("OpenAI", r.status_code == 200, f"HTTP {r.status_code}")
    except Exception as e:
        print_result("OpenAI", False, str(e))
else:
    print("⚠️  AVISO | OpenAI -> Chave vazia no .env")

# Qwen (DashScope)
qwen_key = os.getenv("QWEN_API_KEY")
if qwen_key:
    try:
        # Check through OpenAI compatible endpoint
        r = requests.get("https://dashscope.aliyuncs.com/compatible-mode/v1/models", headers={"Authorization": f"Bearer {qwen_key}"}, timeout=5)
        print_result("Qwen (DashScope)", r.status_code == 200, f"HTTP {r.status_code}")
    except Exception as e:
        print_result("Qwen (DashScope)", False, str(e))
else:
    print("⚠️  AVISO | Qwen -> Chave não encontrada")

# ==========================================
# 2. SERVIÇOS EXTERNOS E APIs
# ==========================================
print("\n--- 🛠️ Serviços Externos ---")

# ElevenLabs
eleven_key = os.getenv("ELEVENLABS_API_KEY")
if eleven_key:
    try:
        r = requests.get("https://api.elevenlabs.io/v1/user", headers={"xi-api-key": eleven_key}, timeout=5)
        print_result("ElevenLabs", r.status_code == 200, f"HTTP {r.status_code}")
    except Exception as e:
        print_result("ElevenLabs", False, str(e))

# HuggingFace
hf_key = os.getenv("HUGGINGFACE_API_KEY")
if hf_key:
    try:
        r = requests.get("https://huggingface.co/api/whoami-v2", headers={"Authorization": f"Bearer {hf_key}"}, timeout=5)
        print_result("HuggingFace", r.status_code == 200, f"HTTP {r.status_code}")
    except Exception as e:
        print_result("HuggingFace", False, str(e))

# Tavily
tavily_key = os.getenv("TAVILY_API_KEY")
if tavily_key:
    try:
        r = requests.post("https://api.tavily.com/search", json={"api_key": tavily_key, "query": "test"}, timeout=5)
        print_result("Tavily", r.status_code == 200, f"HTTP {r.status_code}")
    except Exception as e:
        print_result("Tavily", False, str(e))

# GitHub
github_key = os.getenv("GITHUB_TOKEN")
if github_key:
    try:
        r = requests.get("https://api.github.com/user", headers={"Authorization": f"token {github_key}"}, timeout=5)
        print_result("GitHub", r.status_code == 200, f"HTTP {r.status_code}")
    except Exception as e:
        print_result("GitHub", False, str(e))

# Notion
notion_key = os.getenv("NOTION_API_KEY")
if notion_key:
    try:
        r = requests.get("https://api.notion.com/v1/users/me", headers={"Authorization": f"Bearer {notion_key}", "Notion-Version": "2022-06-28"}, timeout=5)
        print_result("Notion", r.status_code == 200, f"HTTP {r.status_code}")
    except Exception as e:
        print_result("Notion", False, str(e))

# Resend
resend_key = os.getenv("RESEND_API_KEY")
if resend_key:
    try:
        r = requests.get("https://api.resend.com/api-keys", headers={"Authorization": f"Bearer {resend_key}"}, timeout=5)
        print_result("Resend", r.status_code == 200, f"HTTP {r.status_code}")
    except Exception as e:
        print_result("Resend", False, str(e))

# GNews
gnews_key = os.getenv("GNEWS_API_KEY")
if gnews_key:
    try:
        r = requests.get(f"https://gnews.io/api/v4/search?q=example&token={gnews_key}&max=1", timeout=5)
        print_result("GNews", r.status_code == 200, f"HTTP {r.status_code}")
    except Exception as e:
        print_result("GNews", False, str(e))

# OpenWeather
weather_key = os.getenv("OPENWEATHER_API_KEY")
if weather_key:
    try:
        r = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q=London&appid={weather_key}", timeout=5)
        print_result("OpenWeather", r.status_code == 200, f"HTTP {r.status_code}")
    except Exception as e:
        print_result("OpenWeather", False, str(e))

# Z-API (WhatsApp)
zapi_id = os.getenv("ZAPI_INSTANCE_ID")
zapi_token = os.getenv("ZAPI_INSTANCE_TOKEN")
if zapi_id and zapi_token:
    try:
        r = requests.get(f"https://api.z-api.io/instances/{zapi_id}/token/{zapi_token}/status", timeout=5)
        print_result("Z-API (WhatsApp)", r.status_code == 200, f"HTTP {r.status_code}")
    except Exception as e:
        print_result("Z-API (WhatsApp)", False, str(e))

# Asaas
asaas_key = os.getenv("ASAAS_API_KEY")
if asaas_key:
    try:
        domain = "api.asaas.com" if "aact_prod" in asaas_key else "sandbox.asaas.com"
        r = requests.get(f"https://{domain}/api/v3/customers?limit=1", headers={"access_token": asaas_key}, timeout=5)
        print_result("Asaas", r.status_code == 200, f"HTTP {r.status_code}")
    except Exception as e:
        print_result("Asaas", False, str(e))

# ==========================================
# 3. NUVEM E INFRA
# ==========================================
print("\n--- ☁️ Infraestrutura e Nuvem ---")

# Hetzner
hetzner_key = os.getenv("HETZNER_API_KEY")
if hetzner_key:
    try:
        r = requests.get("https://api.hetzner.cloud/v1/servers", headers={"Authorization": f"Bearer {hetzner_key}"}, timeout=5)
        print_result("Hetzner Cloud", r.status_code == 200, f"HTTP {r.status_code}")
    except Exception as e:
        print_result("Hetzner Cloud", False, str(e))

# Postgres
db_url = os.getenv("DATABASE_URL")
if db_url:
    try:
        # Simple port check parsing the URL
        # postgres://user:pass@host:port/db
        host_part = db_url.split("@")[1].split("/")[0]
        host = host_part.split(":")[0]
        port = int(host_part.split(":")[1]) if ":" in host_part else 5432
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        print_result("PostgreSQL (Porta 5432)", result == 0, f"Conexão TCP {'bem-sucedida' if result == 0 else 'falhou'} para {host}")
    except Exception as e:
        print_result("PostgreSQL (Porta 5432)", False, f"Não foi possível parsear URL ou conectar: {str(e)}")

# Cloudflare (CF_API_TOKEN)
cf_token = os.getenv("CF_API_TOKEN")
if cf_token:
    try:
        r = requests.get("https://api.cloudflare.com/client/v4/user/tokens/verify", headers={"Authorization": f"Bearer {cf_token}"}, timeout=5)
        print_result("Cloudflare API", r.status_code == 200 and r.json().get("success"), f"HTTP {r.status_code}")
    except Exception as e:
        print_result("Cloudflare API", False, str(e))

# ==========================================
# 4. VPS & TELEGRAM
# ==========================================
print("\n--- 💻 Acesso Remoto & Bots ---")

# VPS Ping
vps_host = os.getenv("VPS_01_HOST")
if vps_host:
    try:
        response = os.system(f"ping -n 1 {vps_host} > nul 2>&1")
        print_result(f"VPS SSH ({vps_host})", response == 0, "Ping ICMP (Requer acesso de rede)")
    except Exception as e:
        print_result("VPS SSH", False, str(e))

# Telegram
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
if telegram_token:
    try:
        r = requests.get(f"https://api.telegram.org/bot{telegram_token}/getMe", timeout=5)
        print_result("Telegram Bot", r.status_code == 200, f"HTTP {r.status_code}")
    except Exception as e:
        print_result("Telegram Bot", False, str(e))

print("\n🚀 TESTES CONCLUÍDOS 🚀")
