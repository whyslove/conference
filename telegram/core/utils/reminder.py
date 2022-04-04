"""Module to declare reminder."""

from abc import ABC
from time import time
import tzlocal
import asyncio
from datetime import timedelta, datetime
from typing import Dict

from aiogram import Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError
from loguru import logger

from core.database.create_table import SessionLocal
from core.database.repositories.user_speech import UserSpeechRepository
from core.database.repositories.user import UserRepository


def serialize_timedelta(delta: timedelta, locale: str = "ru_RU") -> str:
    if locale != "ru_RU":  # we only need russian, but who knows
        raise ValueError(f"Unsupported locale {locale}")
    delta_str = ":".join(str(delta).split(":")[:2])
    days = delta.days
    if days != 0:
        td_str = delta_str.split()
        if days % 10 == 1:
            day_str = "день"
        elif 2 <= days % 10 <= 4:
            day_str = "дня"
        else:
            day_str = "дней"
        td_str[1] = day_str
        delta_str = " ".join(td_str)
    return delta_str


class BasicReminder(ABC):
    async def send_notification(self, dp: Dispatcher):
        pass

    def add_notification(self, scheduler: AsyncIOScheduler, dp: Dispatcher):
        pass

    def remove_notification(self, scheduler: AsyncIOScheduler):
        pass


class GuestReminder(BasicReminder):
    def __init__(self, chat_id, event: Dict):
        if not chat_id:
            raise TypeError("chat_id must be not empty")
        self.chat_id = chat_id
        self.event = event

    async def send_notification(self, dp: Dispatcher):
        logger.debug(f"Sending notification to {self.chat_id} about {self.event}")
        # deleting seconds and microseconds
        delta = self.event["start_time"] - datetime.now()
        delta_str = serialize_timedelta(delta)
        await dp.bot.send_message(
            self.chat_id,
            f"\"{self.event['title']}\" наступает через {delta_str}",
        )
        await dp.bot.send_message(
            self.chat_id,
            f"Придете ли вы на мероприятие \"{self.event['title']}\"?\n"
            f"Ответьте <b>пойду</b> или <b>не пойду</b>!",
            parse_mode="HTML",
        )
        await dp.storage.set_data(user=self.chat_id, data=self.event)
        await dp.storage.set_state(user=self.chat_id, state="response_guest")

    def callback(self, dp):
        asyncio.ensure_future(self.send_notification(dp))

    def add_notification(self, scheduler: AsyncIOScheduler, dp: Dispatcher):
        logger.debug(f"Adding notification for guest {self.chat_id} and {self.event}")
        scheduler.add_job(
            self.send_notification,
            "date",
            run_date=self.event["start_time"] - timedelta(minutes=15),
            id=str(self.chat_id) + ":" + self.event["key"],
            args=[
                dp,
            ],
        )
        """for job in scheduler.get_jobs():
            logger.debug(f"{job}")"""
        """loop = asyncio.get_event_loop()

        when_to_call = (
            loop.time()
            + (self.event["start_time"] - timedelta(minutes=10) - datetime.now()).total_seconds()
        )
        loop.call_at(when_to_call, self.callback, dp)"""

    def remove_notification(self, scheduler: AsyncIOScheduler):
        logger.debug(f"Removing notification for guest {self.chat_id} and {self.event}")
        try:
            scheduler.remove_job(job_id=str(self.chat_id) + ":" + self.event["key"])
        except JobLookupError:
            pass


class SpeakerReminder(BasicReminder):
    def __init__(self, email, event: Dict):
        if not email:
            raise TypeError("email must be not empty")
        self.email = email
        self.event = event

    async def send_notification(self, dp: Dispatcher):
        logger.debug(f"Sending notification to speaker {self.email} about {self.event}")
        session = SessionLocal()
        user_repo = UserRepository(session)
        user = await user_repo.get_one(self.email)
        chat_id = user["tg_chat_id"]
        if chat_id:
            logger.debug(f"Sending notification to {chat_id} about {self.event}")
            delta = datetime.now() - self.event["start_time"]
            delta_str = serialize_timedelta(delta)
            await dp.bot.send_message(
                chat_id,
                f"{self.event['title']} наступает через {delta_str}",
            )
            await dp.bot.send_message(
                chat_id,
                f"Придете ли вы на мероприятие \"{self.event['title']}\" в качестве спикера?\n"
                f"Напишите, где Вы сейчас находитесь или <b>не пойду</b>!",
                parse_mode="HTML",
            )
            await dp.storage.set_data(user=chat_id, data=self.event)
            await dp.storage.set_state(user=chat_id, state="response_speaker")
        else:
            logger.debug(f"No chat id provided in db for {self.email}")
        await session.close()

    def callback(self, dp):
        asyncio.ensure_future(self.send_notification(dp))

    def add_notification(self, scheduler: AsyncIOScheduler, dp: Dispatcher):
        logger.debug(f"Adding notification for speaker {self.email} and {self.event}")
        scheduler.add_job(
            self.send_notification,
            "date",
            run_date=self.event["start_time"] - timedelta(days=1),
            id=str(self.email) + ":" + self.event["key"] + ":" + "0",
            args=[
                dp,
            ],
        )
        """
        loop = asyncio.get_event_loop()
        when_to_call = (
            loop.time()
            + (self.event["start_time"] - timedelta(minutes=10) - datetime.now()).total_seconds()
        )
        loop.call_at(when_to_call, self.callback, dp)
        """
        scheduler.add_job(
            self.send_notification,
            "date",
            run_date=self.event["start_time"] - timedelta(hours=3),
            id=str(self.email) + ":" + self.event["key"] + ":" + "1",
            args=[
                dp,
            ],
        )
        """
        when_to_call = (
            loop.time()
            + (self.event["start_time"] - timedelta(hours=2) - datetime.now()).total_seconds()
        )
        loop.call_at(when_to_call, self.callback, dp)
        """
        scheduler.add_job(
            self.send_notification,
            "date",
            run_date=self.event["start_time"] - timedelta(minutes=15),
            id=str(self.email) + ":" + self.event["key"] + ":" + "2",
            args=[
                dp,
            ],
        )
        """
        when_to_call = (
            loop.time()
            + (self.event["start_time"] - timedelta(hours=2) - datetime.now()).total_seconds()
        )
        loop.call_at(when_to_call, self.callback, dp)
        """

    def remove_notification(self, scheduler: AsyncIOScheduler):
        logger.debug(f"Removing notification for speakers {self.email} and {self.event}")
        for num in range(3):
            try:
                scheduler.remove_job(
                    job_id=str(self.email) + ":" + self.event["key"] + ":" + str(num)
                )
            except JobLookupError:
                pass


class ModeratorReminder(BasicReminder):
    def __init__(self, event):
        self.event = event

    async def send_notification(self, dp: Dispatcher):
        logger.debug(f"Sending notification to moderators about events")
        session = SessionLocal()
        user_repo = UserRepository(session)
        moderators_list = await user_repo.get_all(is_admin=True)
        user_speech_repo = UserSpeechRepository(session)
        user_speech_list = await user_speech_repo.get_all(key=self.event["key"])
        sorted(user_speech_list, key=lambda user_speech: (user_speech["role"], user_speech["uid"]))
        # send data to several moderators
        for moderator in moderators_list:
            if moderator:
                # send data to moderator
                if moderator["tg_chat_id"]:
                    await dp.bot.send_message(moderator["tg_chat_id"], "Ответы всех участников:")
                    for user_speech in user_speech_list:
                        user = await user_repo.get_one(uid=user_speech["uid"])
                        acknowledgment = user_speech["acknowledgment"]
                        if acknowledgment:
                            await dp.bot.send_message(
                                moderator["tg_chat_id"],
                                f"{user['snp']}: {'спикер' if user_speech['role'] == '1' else 'гость'} написал: \"{acknowledgment}\" о мероприятии <b>\"{self.event['title']}\"</b>",
                                parse_mode="HTML",
                            )
                        else:
                            await dp.bot.send_message(
                                moderator["tg_chat_id"],
                                f"{user['snp']}: {'спикер' if user_speech['role'] == '1' else 'гость'} ничего не написал о мероприятии <b>\"{self.event['title']}\"</b>",
                                parse_mode="HTML",
                            )
                else:
                    logger.debug(f"No tg_chat_id for moderator {moderator}")
        await session.close()

    def callback(self, dp):
        asyncio.ensure_future(self.send_notification(dp))

    def add_notification(self, scheduler: AsyncIOScheduler, dp: Dispatcher):
        scheduler.add_job(
            self.send_notification,
            "date",
            run_date=self.event["start_time"] - timedelta(minutes=10),
            args=[
                dp,
            ],
        )
        """
        loop = asyncio.get_event_loop()
        when_to_call = (
            loop.time()
            + (self.event["start_time"] - timedelta(minutes=5) - datetime.now()).total_seconds()
        )
        loop.call_at(when_to_call, self.callback, dp)
        """

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
        self.scheduler = AsyncIOScheduler(timezone=tz)  # event_loop=asyncio.get_event_loop())
        self.dp = dp
        # self.scheduler.start()
        logger.debug("Scheduler was initialized successfully")

    def start(self):
        logger.debug("Starting scheduler")
        self.scheduler.start()
        logger.debug("Scheduler started")

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
