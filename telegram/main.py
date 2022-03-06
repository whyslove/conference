"""Module to declare fastApi web server to get webhooks from telegram."""
import uvicorn

from aiogram import types, Dispatcher, Bot
from fastapi import FastAPI

from core.config import config
from core.config import bot, dp
from core import handlers
from core import filters


app = FastAPI()

WEBHOK_PATH = "/bot"


@app.on_event("startup")
async def on_startup():
    """Initializes filters, middlewares, hadlers and webhook."""
    await bot.set_webhook(url=config.WEBHOOK_URL + WEBHOK_PATH)
    filters.setup(dp)
    handlers.setup(dp)


@app.post(WEBHOK_PATH)
async def bot_webhook(update: dict):
    """Process update from tg

    Args:
        update (dict): update from tg
    """
    telegram_update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(telegram_update)


@app.on_event("shutdown")
async def on_shutdown():
    """Closes all connections."""
    await dp.bot.close()
    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
