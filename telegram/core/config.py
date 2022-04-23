import aioredis

from pydantic import BaseSettings
from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from core.utils.reminder import Scheduler
from jinja2 import Environment, FileSystemLoader, select_autoescape


class Settings(BaseSettings):
    WEBHOOK_URL: str
    TELEGRAM_SECRET: str
    DB_PATH: str
    JOB_STORE_HOST: str
    JOB_STORE_PORT: str
    TELEGRAPH_TOKEN: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    VERIFICATION_URL: str

    class Config:
        env_file = "./telegram/.env"


config = Settings()

storage = MemoryStorage()
bot = Bot(token=config.TELEGRAM_SECRET)
dp = Dispatcher(bot, storage=storage)
jinja_env = Environment(
    loader=FileSystemLoader("./telegram/core/utils/html_templates"), autoescape=select_autoescape()
)
# from apscheduler.jobstores.redis import RedisJobStore
# from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
# from apscheduler.executors.pool import ThreadPoolExecutor

# jobstores = {
#     "default": RedisJobStore(host=config.JOB_STORE_HOST, port=config.JOB_STORE_PORT, db=13)
# }
# jobstores = {"default": SQLAlchemyJobStore(url="sqlite:///jobs.sqlite")}
# executors = {"default": ThreadPoolExecutor(10)}
redis = aioredis.from_url("redis://redis", decode_responses=True)  # lazy?
job_defaults = {"coalesce": False, "max_instances": 5}
sc = Scheduler(dp)
