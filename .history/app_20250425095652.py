import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import uuid

# Logging konfiqurasiyası
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot tokeni (BotFather-dən alınan tokeni bura daxil edin)
TOKEN = "7776707741:AAF_ZKRfjt-yGn2fYJVwXfCQZtg95vaAxDA"

# MP3 çevirmə funksiyası
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
            'noplaylist': True,  # Playlistləri dəstəkləmir, yalnız tək video
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            return True, filename, info['title']
    except Exception as e:
        logger.error(f"MP3 çevirmə xətası: {e}")
        return False, None, None

# /start əmri
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salam! Mən YouTube videolarını MP3 formatına çevirən botam. "
        "Sadəcə YouTube linkini göndər, mən sənə MP3 faylını göndərəcəm! 🎵"
    )

# Linkləri emal etmək üçün funksiya
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text

    # YouTube linkini yoxla
    if "youtube.com" not in message_text and "youtu.be" not in message_text:
        await update.message.reply_text("Xahiş edirəm, düzgün YouTube linki göndərin!")
        return

    await update.message.reply_text("Link qəbul edildi. MP3 çevirməsi başlayır, zəhmət olmasa gözləyin... ⏳")

    # Unikal fayl adı üçün UUID istifadə et
    output_path = f"downloads/{uuid.uuid4()}"
    os.makedirs(output_path, exist_ok=True)

    # MP3 çevirmə
    success, filename, title = await download_and_convert_to_mp3(message_text, output_path)

    if success and filename and os.path.exists(filename):
        try:
            # MP3 faylını göndər
            with open(filename, 'rb') as audio:
                await update.message.reply_audio(
                    audio=audio,
                    title=title,
                    caption=f"{title} - Uğurla çevrildi! 🎧"
                )
            await update.message.reply_text("MP3 faylı göndərildi! Başqa link göndərə bilərsiniz.")
        except Exception as e:
            logger.error(f"Fayl göndərmə xətası: {e}")
            await update.message.reply_text("Faylı göndərərkən xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.")
        finally:
            # Faylı və qovluğu sil
            try:
                os.remove(filename)
                os.rmdir(output_path)
            except Exception as e:
                logger.warning(f"Fayl silinmə xətası: {e}")
    else:
        await update.message.reply_text(
            "Üzr istəyirik, linki MP3 formatına çevirmək mümkün olmadı. "
            "Linkin düzgün olduğundan əmin olun və ya başqa link cəhd edin."
        )

# Xəta idarəetmə
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Xəta baş verdi: {context.error}")
    if update and update.message:
        await update.message.reply_text(
            "Üzr istəyirik, botda xəta baş verdi. Zəhmət olmasa yenidən cəhd edin."
        )

def main():
    # Botu başlat
    app = Application.builder().token(TOKEN).build()

    # Əmrlər və mesaj handlerləri
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    # Botu işə sal
    logger.info("Bot işə salındı...")
    app.run_polling()

if __name__ == '__main__':
    main()