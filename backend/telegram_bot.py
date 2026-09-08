"""
Integração nativa com Telegram.
Permite conversar com o ALFRED através de um chat seguro.
"""
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import settings
from models import Task
from router import TaskRouter
import uuid
from datetime import datetime

# Inicializa as variáveis mas só inicia o bot se tiver o Token
bot = None
dp = Dispatcher()
alfred_router = None

if settings.TELEGRAM_BOT_TOKEN:
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

async def process_telegram_message(message: types.Message):
    """Filtra mensagens para garantir que são apenas do dono."""
    if str(message.chat.id) != settings.TELEGRAM_CHAT_ID:
        await message.answer("⚠️ Acesso Negado. Você não está autorizado a interagir com este núcleo A.L.F.R.E.D.")
        return

    # Manda um 'digitando...' para dar feedback imediato
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    # Cria a Tarefa e manda pro cérebro
    task = Task(
        id=f"tg-{uuid.uuid4().hex[:8]}",
        command=message.text,
        context={"source": "telegram", "chat_id": message.chat.id}
    )
    
    try:
        result = await alfred_router.execute(task)
        
        # O limite do telegram é ~4096 caracteres. Se for gigante, divide.
        output = result.output
        if len(output) > 4000:
            await message.answer(output[:4000] + "\n\n[... Truncado ...]")
        else:
            await message.answer(output)
            
    except Exception as e:
        await message.answer(f"❌ Erro Crítico do Orquestrador: {str(e)}")

@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    """Mensagem inicial ao dar /start"""
    if str(message.chat.id) != settings.TELEGRAM_CHAT_ID:
        await message.answer("Acesso Negado.")
        return
    await message.answer("📡 **A.L.F.R.E.D. Conexão Estabelecida.**\nAguardando comandos, senhor.")

@dp.message()
async def handle_text(message: types.Message):
    """Escuta tudo que for digitado no chat."""
    await process_telegram_message(message)

async def start_telegram_bot(main_router: TaskRouter):
    """Inicia o Long Polling silenciosamente no fundo do FastAPI."""
    global alfred_router
    alfred_router = main_router
    
    if not bot:
        print("[TELEGRAM] Token ausente. Bot desativado.")
        return
        
    if not settings.TELEGRAM_CHAT_ID:
        print("[TELEGRAM] ATENÇÃO: TELEGRAM_CHAT_ID não configurado. Bot não responderá a ninguém por segurança.")
        
    print("[TELEGRAM] 🤖 Bot Online e ouvindo.")
    await dp.start_polling(bot)
