import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

API_URL = "https://api.ytdlp.online/api/json"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Drop a YouTube (or other platform) link and I’ll fetch your video 🎥")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    await update.message.reply_text("⏳ Working on it... hold tight.")

    try:
        # Ask YT-DLP API for download info
        response = requests.post(API_URL, json={"url": url})
        data = response.json()

        # Check if response has the video URL
        if "url" not in data:
            await update.message.reply_text("⚠️ Couldn't get the download link. Try another URL.")
            return

        video_url = data["url"]
        title = data.get("title", "video")
        file_name = f"{title}.mp4"

        # Download the video file
        r = requests.get(video_url, stream=True)
        file_path = os.path.join("/tmp", file_name)

        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        # Send the video file to user
        await update.message.reply_video(video=open(file_path, "rb"), caption=f"🎬 {title}")

        # Clean up
        os.remove(file_path)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

def main():
    app = ApplicationBuilder().token("YOUR_TELEGRAM_BOT_TOKEN").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
