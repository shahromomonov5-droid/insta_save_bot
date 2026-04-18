import os
import logging
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Bot token
BOT_TOKEN = "8655631642:AAGWpq3kbx2Cp6k9PyeVPcrQ5BUbVXrbJas"

# Logging sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom! Men Instagram video yuklovchi botman.\n\n"
        "📌 Ishlatish:\n"
        "Instagram post yoki reel havolasini yuboring, men videoni yuklab beraman!\n\n"
        "Misol: https://www.instagram.com/reel/xxxxx/"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Yordam:\n\n"
        "1. Instagram post/reel havolasini ko'chiring\n"
        "2. Shu havolani menga yuboring\n"
        "3. Men videoni yuklab jo'nataman!\n\n"
        "⚠️ Faqat ochiq (public) akkauntlar ishlaydi."
    )


async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    # Instagram URL tekshirish
    if "instagram.com" not in url:
        await update.message.reply_text("❌ Iltimos, Instagram havolasini yuboring!")
        return

    msg = await update.message.reply_text("⏳ Video yuklanmoqda, kuting...")

    try:
        # Yuklash papkasi
        download_path = "./downloads"
        os.makedirs(download_path, exist_ok=True)

        ydl_opts = {
            'outtmpl': f'{download_path}/%(id)s.%(ext)s',
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # Faylni Telegramga jo'natish
        await msg.edit_text("📤 Video jo'natilmoqda...")

        with open(filename, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption="✅ Mana sizning videongiz!\n\n🤖 @YourBotUsername"
            )

        await msg.delete()

        # Faylni o'chirish
        os.remove(filename)

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Download error: {e}")
        await msg.edit_text(
            "❌ Video yuklab bo'lmadi!\n\n"
            "Sabablari:\n"
            "• Akkaunt yopiq (private) bo'lishi mumkin\n"
            "• Havola noto'g'ri\n"
            "• Instagram cheklov qo'ygan\n\n"
            "Qayta urinib ko'ring!"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await msg.edit_text("❌ Xatolik yuz berdi! Qayta urinib ko'ring.")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    logger.info("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
