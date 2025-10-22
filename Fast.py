from fastapi import FastAPI
import threading
import os
from telegram.ext import ApplicationBuilder

app = FastAPI()

@app.get("/")
def home():
    return {"status": "bot running"}

def run_bot():
    import bot  # запускаем бота в отдельном потоке

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
