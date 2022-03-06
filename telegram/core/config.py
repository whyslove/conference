from pydantic import BaseSettings
from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from core.utils.reminder import Scheduler
from apscheduler.executors.pool import ThreadPoolExecutor


class Settings(BaseSettings):
    WEBHOOK_URL: str
    TELEGRAM_SECRET: str
    DB_PATH: str
    JOB_STORE_HOST: str
    JOB_STORE_PORT: str

    class Config:
        env_file = "./telegram/.env"


config = Settings()

storage = MemoryStorage()
bot = Bot(token=config.TELEGRAM_SECRET)
dp = Dispatcher(bot, storage=storage)
jobstores = {"default": RedisJobStore(host=config.JOB_STORE_HOST, port=config.JOB_STORE_PORT, db=13)}
jobstores = {"default": SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')}
executors = {
            "default": ThreadPoolExecutor(10)
        }
job_defaults = {
            "coalesce": False,
            "max_instances": 5
        }
sc = Scheduler(dp)
