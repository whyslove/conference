"""Module to declare reminder."""
import tzlocal
import asyncio
from datetime import timedelta, datetime
from typing import Dict
from aiogram import Dispatcher
from abc import ABC
from loguru import logger
from core import config
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError
from core.database.create_table import SessionLocal
from core.database.repositories.user_speech import UserSpeechRepository
from core.database.repositories.user import UserRepository


class BasicReminder(ABC):
    async def send_notification(self, dp: Dispatcher):
        pass

    def add_notification(self, scheduler: AsyncIOScheduler, dp: Dispatcher):
        pass

    def remove_notification(self, scheduler: AsyncIOScheduler):
        pass


class GuestReminder(BasicReminder):
    def __init__(self, chat_id, event: Dict):
        self.chat_id = chat_id
        self.event = event

    async def send_notification(self, dp: Dispatcher):
        logger(f"Sending notification to {self.chat_id} about {self.event}")
        await dp.bot.send_message(
            self.chat_id,
            f"{self.event['title']} наступает через {datetime.now() - self.event['start_time']}",
        )
        await dp.bot.send_message(
            self.chat_id,
            f"Будете ли вы на {self.event['title']}\
        Напишите Буду, если намереваетесь придти и Не буду, если не придете",
        )
        await dp.storage.set_data(user=self.chat_id, data=self.event)
        await dp.storage.set_state(user=self.chat_id, state="response_guest")

    def add_notification(self, scheduler: AsyncIOScheduler, dp: Dispatcher):
        logger.debug(f"Adding notification for guest {self.chat_id} and {self.event}")
        scheduler.add_job(
            self.send_notification,
            "date",
            run_date=self.event["start_time"] - timedelta(minutes=1),
            id=str(self.chat_id) + ":" + self.event["key"],
            args=[
                dp,
            ],
        )
        for job in scheduler.get_jobs():
            logger.debug(f"{job}")

    def remove_notification(self, scheduler: AsyncIOScheduler):
        logger.debug(f"Removing notification for guest {self.chat_id} and {self.event}")
        try:
            scheduler.remove_job(job_id=str(self.chat_id) + ":" + self.event["key"])
        except JobLookupError:
            pass


class SpeakerReminder(BasicReminder):
    def __init__(self, chat_id, event: Dict):
        self.chat_id = chat_id
        self.event = event

    async def send_notification(self, dp: Dispatcher):
        logger(f"Sending notification to {self.chat_id} about {self.event}")
        dp.bot.send_message(
            self.chat_id,
            f"{self.event['title']} наступает через {datetime.now() - self.event['start_time']}",
        )
        await dp.bot.send_message(
            self.chat_id,
            f"Будете ли вы на {self.event['title']}\
        Напишите где находитесь, если намереваетесь придти и Отказываюсь, если не придете",
        )
        await dp.storage.set_data(user=self.chat_id, data=self.event)
        await dp.storage.set_state(user=self.chat_id, state="response_speaker")

    def add_notification(self, scheduler: AsyncIOScheduler, dp: Dispatcher):
        logger.debug(f"Removing notification for guest {self.chat_id} and {self.event}")
        scheduler.add_job(
            self.send_notification,
            "date",
            run_date=self.event["start_time"] - timedelta(days=1),
            id=str(self.chat_id) + ":" + self.event["key"] + ":" + "0",
            args=[
                dp,
            ],
        )
        scheduler.add_job(
            self.send_notification,
            "date",
            run_date=self.event["start_time"] - timedelta(hours=3),
            id=str(self.chat_id) + ":" + self.event["key"] + ":" + "1",
            args=[
                dp,
            ],
        )
        scheduler.add_job(
            self.send_notification,
            "date",
            run_date=self.event["start_time"] - timedelta(minutes=10),
            id=str(self.chat_id) + ":" + self.event["key"] + ":" + "2",
            args=[
                dp,
            ],
        )

    def remove_notification(self, scheduler: AsyncIOScheduler):
        logger.debug(f"Removing notification for speakers {self.chat_id} and {self.event}")
        for num in range(3):
            try:
                scheduler.remove_job(
                    job_id=str(self.chat_id) + ":" + self.event["key"] + ":" + str(num)
                )
            except JobLookupError:
                pass


class ModeratorReminder(BasicReminder):
    def __init__(self, chat_id, event):
        self.chat_id = chat_id
        self.event = event

    async def send_notification(self, dp: Dispatcher):
        logger(f"Sending notification to {self.chat_id} about events")
        session = SessionLocal()
        user_speech_repo = UserSpeechRepository(session)
        user_speech_list = await user_speech_repo.get_all(role="1", key=self.event["key"])
        for user_speech in user_speech_list:
            user_repo = UserRepository(session)
            user = await user_repo.get_one(uid=user_speech["uid"])
            acknowledgment = user_speech["acknowledgment"]
            await dp.bot.send_message(
                self.chat_id, f"{user['snp']} {self.event['title']} {acknowledgment}"
            )

        session.close()

    def add_notification(self, scheduler: AsyncIOScheduler, dp: Dispatcher):
        scheduler.add_job(
            self.send_notification,
            "date",
            run_date=self.event["start_time"] - timedelta(minutes=10),
            args=[
                dp,
            ],
        )

    def remove_notification(self, scheduler: AsyncIOScheduler):
        pass


class Scheduler:
    def __init__(self, dp: Dispatcher):
        logger.debug("Initializing scheduler")
        tz = tzlocal.get_localzone()
        """self.scheduler = AsyncIOScheduler(
            timezone=tz,
            jobstores=config.jobstores,
            executors=config.executors,
            job_defaults=config.job_defaults,
        )"""
        self.scheduler = AsyncIOScheduler(timezone=tz)
        self.dp = dp
        self.scheduler.start()
        logger.debug("Scheduler was initialized successfully")

    def add_remind(self, reminder: BasicReminder):
        reminder.add_notification(self.scheduler, self.dp)

    def remove_remind(self, reminder: BasicReminder):
        reminder.remove_notification(self.scheduler)


"""
scheduler = Scheduler(None)

gs = GuestReminder(
    "13234",
    {
        "title": "sit amet cursus",
        "start_time": "2019-09-02 14:07:53",
        "end_time": "2021-11-01 18:04:51",
        "venue": "semper sapien",
        "venue_description": "sociis natoque penatibus et magnis dis parturient montes nascetur ridiculus mus vivamus vestibulum sagittis",
    },
)
scheduler.add_remind(gs)
"""
