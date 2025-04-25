import logging
import os
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import yt_dlp
import asyncio
import re

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram Bot Token
TOKEN = "7776707741:AAF_ZKRfjt-yGn2fYJVwXfCQZtg95vaAxDA"

# Webhook ayarları
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://ytdownlaoder.onrender.com{WEBHOOK_PATH}"
# Render PORT çevre değişkenini kullanıyor, varsayılan olarak 8443
PORT = int(os.getenv("PORT", 8443))

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def download_audio(url: str, output_path: str) -> tuple:
    try:
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return True, filename, info['title']
    except Exception as e:
        logger.error(f"Audio yükləmə xətası: {e}")
        return False, None, None

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "Salam! Mən YouTube videolarını audio formatına çevirən botam. "
        "Sadəcə YouTube linkini göndər, mən sənə audio faylını göndərəcəm! 🎵"
    )

async def is_youtube_link(text: str) -> bool:
    youtube_regex = r'(https?://)?(www\.)?(youtube\.com|m\.youtube\.com|youtu\.be)/.+'
    return bool(re.match(youtube_regex, text))

@dp.message()
async def handle_message(message: types.Message):
    text = message.text

    if await is_youtube_link(text):
        await message.answer("Link qəbul edildi. Audio yüklənməsi başlayır, zəhmət olmasa gözləyin... ⏳")

        output_path = f"downloads/{uuid.uuid4()}"
        os.makedirs(output_path, exist_ok=True)

        success, filename, title = await download_audio(text, output_path)

        if success and filename and os.path.exists(filename):
            try:
                audio = FSInputFile(filename, filename=os.path.basename(filename))
                await message.answer_audio(
                    audio=audio,
                    title=title,
                    caption=f"{title} - Uğurla yükləndi! 🎧"
                )
                await message.answer("Audio faylı göndərildi! Başqa link göndərə bilərsiniz.")
            except Exception as e:
                logger.error(f"Fayl göndərmə xətası: {e}")
                await message.answer("Faylı göndərərkən xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.")
            finally:
                try:
                    os.remove(filename)
                    os.rmdir(output_path)
                except Exception as e:
                    logger.warning(f"Fayl silinmə xətası: {e}")
        else:
            await message.answer(
                "Üzr istəyirik, linki audio formatına yükləmək mümkün olmadı. "
                "Linkin düzgün olduğundan əmin olun və ya başqa link cəhd edin."
            )
    else:
        await message.answer("Xahiş edirəm, düzgün YouTube linki göndərin!")

async def on_startup(_):
    # Webhook'u ayarla
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook set to {WEBHOOK_URL}")

async def on_shutdown(_):
    # Webhook'u kaldır ve bot oturumunu kapat
    await bot.delete_webhook()
    await bot.session.close()
    logger.info("Bot shutdown")

async def main():
    logger.info("Bot işə salındı...")
    # aiohttp web sunucusu oluştur
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    # Startup ve shutdown olaylarını kaydet
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Web sunucusunu başlat
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logger.info(f"Server started on port {PORT}")

    # Süresiz çalış
    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()

if __name__ == '__main__':
    asyncio.run(main())