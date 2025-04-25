import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Telegram bot tokeni
TOKEN = "7776707741:AAF_ZKRfjt-yGn2fYJVwXfCQZtg95vaAxDA"

# YouTube linkindən mp3 faylı yükləmək üçün funksiya
def youtube_to_mp3(url, file_name="audio"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{file_name}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return f"{file_name}.mp3"

# /start komandası
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salam! Mən YouTube linkindən MP3 yükləyən botam. Sadəcə linki göndərin.")

# Gələn mesaj (link) işlənməsi
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    # Sadə yoxlama
    if not url.startswith("http"):
        await update.message.reply_text("Zəhmət olmasa düzgün YouTube linki göndərin.")
        return

    await update.message.reply_text("Yüklənir... Bir az gözləyin.")

    try:
        file_name = f"audio_{update.message.chat.id}"
        mp3_file = youtube_to_mp3(url, file_name)

        with open(mp3_file, 'rb') as audio:
            await update.message.reply_audio(audio)

        os.remove(mp3_file)

    except Exception as e:
        await update.message.reply_text(f"Xəta baş verdi: {str(e)}")

# Botun əsas işləmə mexanizmi
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot işə salındı...")
    await app.run_polling()

# Botu işə salırıq
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
