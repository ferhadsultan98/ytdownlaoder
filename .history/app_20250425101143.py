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
dp = Dispatcher()d

async def download_and_convert_to_mp3(url: str, output_path: str) -> tuple:
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            return True, filename, info['title']
    except Exception as e:
        logger.error(f"MP3 çevirmə xətası: {e}")
        return False, None, None

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "Salam! Mən YouTube videolarını MP3 formatına çevirən botam. "
        "Sadəcə YouTube linkini göndər, mən sənə MP3 faylını göndərəcəm! 🎵"
    )

async def is_youtube_link(text: str) -> bool:
    youtube_regex = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'
    return bool(re.match(youtube_regex, text))

@dp.message()
async def handle_message(message: types.Message):
    text = message.text

    if await is_youtube_link(text):
        await message.answer("Link qəbul edildi. MP3 çevirməsi başlayır, zəhmət olmasa gözləyin... ⏳")

        output_path = f"downloads/{uuid.uuid4()}"
        os.makedirs(output_path, exist_ok=True)

        success, filename, title = await download_and_convert_to_mp3(text, output_path)

        if success and filename and os.path.exists(filename):
            try:
                audio = FSInputFile(filename, filename=os.path.basename(filename))
                await message.answer_audio(
                    audio=audio,
                    title=title,
                    caption=f"{title} - Uğurla çevrildi! 🎧"
                )
                await message.answer("MP3 faylı göndərildi! Başqa link göndərə bilərsiniz.")
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
                "Üzr istəyirik, linki MP3 formatına çevirmək mümkün olmadı. "
                "Linkin düzgün olduğundan əmin olun və ya başqa link cəhd edin."
            )
    else:
        await message.answer("Xahiş edirəm, düzgün YouTube linki göndərin!")

async def main():
    logger.info("Bot işə salındı...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())