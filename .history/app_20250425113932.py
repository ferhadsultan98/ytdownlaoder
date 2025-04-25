import logging
import os
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile
import yt_dlp
import asyncio
import re

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "7776707741:AAF_ZKRfjt-yGn2fYJVwXfCQZtg95vaAxDA"

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
 raff
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

async def main():
    logger.info("Bot işə salındı...")
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())