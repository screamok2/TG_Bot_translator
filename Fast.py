from fastapi import FastAPI
from threading import Thread
from bot import run_bot  # твоя функция, запускающая polling

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

# Запуск бота в отдельном потоке
Thread(target=run_bot).start()
