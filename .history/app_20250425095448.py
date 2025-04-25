import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Telegram bot tokeninizi burada yerləşdirin
TOKEN = 'YOUR_BOT_TOKEN'

# MP3 formatında YouTube video yükləmə funksiyası
async def download_mp3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Istifadəçinin göndərdiyi YouTube linkini alırıq
    url = ' '.join(context.args)  # URL istifadəçi tərəfindən komandada verilməli

    # YT-DLP parametrləri
    ydl_opts = {
        'format': 'bestaudio/best',  # Ən yaxşı səs keyfiyyətini seçirik
        'postprocessors': [{
            'key': 'FFmpegAudio',
            'preferredcodec': 'mp3',  # MP3 formatına çevirmək
            'preferredquality': '192',  # Keyfiyyət
        }],
        'outtmpl': 'downloads/%(id)s.%(ext)s',  # Yükləmənin saxlanacağı yer
    }

    try:
        # YT-DLP ilə video yüklənməsi
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get('title', None)

        # Yüklənmiş MP3 faylını Telegram'a göndəririk
        file_path = f'downloads/{info_dict["id"]}.mp3'
        await update.message.reply_audio(audio=open(file_path, 'rb'))

    except Exception as e:
        await update.message.reply_text(f'Xəta baş verdi: {e}')

# Botu qurmaq üçün əsas funksiya
async def main():
    app = Application.builder().token(TOKEN).build()

    # Komanda handleri
    app.add_handler(CommandHandler("download", download_mp3))

    # Botu işə salmaq
    await app.run_polling()

# Botu başlatmaq
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
