# file: main.py
import os
import threading
from fastapi import FastAPI
import uvicorn
from telegram.ext import ApplicationBuilder, CommandHandler

app = FastAPI()

@app.get("/")
def home():
    return {"status": "bot is running"}

# --- Telegram bot setup ---
async def start(update, context):
    await update.message.reply_text("Бот работает!")

def run_bot():
    from telegram.ext import ApplicationBuilder, CommandHandler
    TOKEN = os.getenv("BOT_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    threading.Thread(target=run_bot).start()

    # Запускаем FastAPI (Render требует открытый порт)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
