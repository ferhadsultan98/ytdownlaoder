import os
import logging
import sys
from pytube import YouTube

# Önce telegram-bot kütüphanenizin versiyonunu tespit edelim
try:
    import telegram
    print(f"Telegram kütüphanesi sürümü: {telegram.__version__}")

    # Telegram sürümüne göre doğru importları yapın
    if telegram.__version__.startswith('13.'):
        # Telegram 13.x için
        from telegram import Update
        from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
        
        # Bot token
        TOKEN = "7776707741:AAF_ZKRfjt-yGn2fYJVwXfCQZtg95vaAxDA"
        
        def start(update, context):
            update.message.reply_text("Merhaba! YouTube linklerini bana gönder, ben MP3 olarak indireceğim.")
        
        def help_command(update, context):
            update.message.reply_text("YouTube linkini gönder, ben MP3 olarak indirip sana göndereceğim.")
        
        def download_youtube(update, context):
            message_text = update.message.text
            
            if "youtube.com" in message_text or "youtu.be" in message_text:
                update.message.reply_text("MP3 indiriliyor, lütfen bekleyin...")
                
                try:
                    # YouTube video indirme işlemi
                    yt = YouTube(message_text)
                    audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
                    
                    if not os.path.exists('temp'):
                        os.makedirs('temp')
                    
                    file_path = audio_stream.download(output_path='temp')
                    base, ext = os.path.splitext(file_path)
                    mp3_file = base + '.mp3'
                    os.rename(file_path, mp3_file)
                    
                    # Dosyayı gönder
                    context.bot.send_audio(
                        chat_id=update.effective_chat.id,
                        audio=open(mp3_file, 'rb'),
                        title=yt.title,
                        performer=yt.author
                    )
                    
                    os.remove(mp3_file)
                    
                except Exception as e:
                    logging.error(f"Hata: {str(e)}")
                    update.message.reply_text(f"Hata oluştu: {str(e)}")
            else:
                update.message.reply_text("Lütfen geçerli bir YouTube linki gönderin.")
        
        def main():
            updater = Updater(TOKEN, use_context=True)
            dp = updater.dispatcher
            
            dp.add_handler(CommandHandler("start", start))
            dp.add_handler(CommandHandler("help", help_command))
            dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download_youtube))
            
            updater.start_polling()
            updater.idle()
            
    elif telegram.__version__.startswith('20.'):
        # Telegram 20.x için (async API)
        from telegram import Update
        from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
        
        # Bot token
        TOKEN = "7776707741:AAF_ZKRfjt-yGn2fYJVwXfCQZtg95vaAxDA"
        
        async def start(update, context):
            await update.message.reply_text("Merhaba! YouTube linklerini bana gönder, ben MP3 olarak indireceğim.")
        
        async def help_command(update, context):
            await update.message.reply_text("YouTube linkini gönder, ben MP3 olarak indirip sana göndereceğim.")
        
        async def download_youtube(update, context):
            message_text = update.message.text
            
            if "youtube.com" in message_text or "youtu.be" in message_text:
                await update.message.reply_text("MP3 indiriliyor, lütfen bekleyin...")
                
                try:
                    # YouTube video indirme işlemi
                    yt = YouTube(message_text)
                    audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
                    
                    if not os.path.exists('temp'):
                        os.makedirs('temp')
                    
                    file_path = audio_stream.download(output_path='temp')
                    base, ext = os.path.splitext(file_path)
                    mp3_file = base + '.mp3'
                    os.rename(file_path, mp3_file)
                    
                    # Dosyayı gönder
                    await update.message.reply_audio(
                        audio=open(mp3_file, 'rb'),
                        title=yt.title,
                        performer=yt.author
                    )
                    
                    os.remove(mp3_file)
                    
                except Exception as e:
                    logging.error(f"Hata: {str(e)}")
                    await update.message.reply_text(f"Hata oluştu: {str(e)}")
            else:
                await update.message.reply_text("Lütfen geçerli bir YouTube linki gönderin.")
        
        def main():
            application = Application.builder().token(TOKEN).build()
            
            application.add_handler(CommandHandler("start", start))
            application.add_handler(CommandHandler("help", help_command))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_youtube))
            
            application.run_polling()
            
    else:
        # Diğer sürümler için daha genel bir yaklaşım
        print("Telegram kütüphanenizin sürümü desteklenmiyor. Lütfen python-telegram-bot'u tekrar yükleyin.")
        print("Aşağıdaki komutla yükleyebilirsiniz:")
        print("pip install python-telegram-bot==13.13")
        sys.exit(1)

except ImportError:
    print("Telegram kütüphanesi bulunamadı veya sürüm bilgisi alınamadı.")
    print("Lütfen şu komutu çalıştırın:")
    print("pip install python-telegram-bot==13.13")
    sys.exit(1)

if __name__ == "__main__":
    main()