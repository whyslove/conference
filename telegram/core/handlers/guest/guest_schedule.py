"""Module to illustrate personal schedule."""

from datetime import datetime, timedelta
from aiogram import types
from click import option
from loguru import logger
from core.keyboards.all_keyboards import all_keyboards
from core.database.repositories.speech import SpeechRepository
from core.database.create_table import SessionLocal
from core.database.repositories.user_speech import UserSpeechRepository
from core.database.repositories.user import UserRepository


async def personal_schedule(message: types.Message):
    """Choosing personal schedule

    :param message: Message instance
    :type message: types.Message
    """
    logger.debug(f"In personal schedule for guest {message.from_user}")
    await message.answer("Выберите опцию", reply_markup=all_keyboards["guest_personal_schedule"]())


async def show_personal_schedule_today(message: types.Message):
    """Answers personal schedule for today

    :param message: Message instance
    :type message: types.Message
    """
    logger.debug(f"In show personal schedule for today for guest {message.from_user}")
    await message.answer("Расписание на сегодня")
    session = SessionLocal()
    user_speech_repo = UserSpeechRepository(session)
    user_repo = UserRepository(session)
    user = await user_repo.get_one(tg_chat_id=message.from_user.id)
    if user:
        user_speech_list = await user_speech_repo.get_all(user["uid"], role="0")
        for user_speech in user_speech_list:
            speech_repo = SpeechRepository(session=session)
            event = await speech_repo.get_one(key=user_speech["key"])
            if event["start_time"].date() == datetime.today().date():
                title = event["title"]
                begin_date = event["start_time"]
                end_date = event["end_time"]
                venue = event["venue"]
                venue_description = event["venue_description"]
                await message.answer(
                    f"""Мероприятие: {title}
                Начало: {begin_date}
                Конец: {end_date}
                Место: {venue}
                Описание: {venue_description}
                Пойдешь?""",
                    reply_markup=all_keyboards["remove_event"](event["key"]),
                )
    else:
        logger.debug(f"Can't find user with {message.from_user.id} tel id")
    await session.close()


async def show_personal_schedule_tomorrow(message: types.Message):
    """Answers personal schedule for tomorrow

    :param message: Message instance
    :type message: types.Message
    """
    logger.debug(f"In show personal schedule for tomorrow for guest {message.from_user}")
    await message.answer("Расписание на завтра")
    session = SessionLocal()
    user_speech_repo = UserSpeechRepository(session)
    user_repo = UserRepository(session)
    user = await user_repo.get_one(tg_chat_id=message.from_user.id)
    if user:
        user_speech_list = await user_speech_repo.get_all(user["uid"], role="0")
        for user_speech in user_speech_list:
            speech_repo = SpeechRepository(session=session)
            event = await speech_repo.get_one(key=user_speech["key"])
            if event["start_time"].date() == datetime.today().date() + timedelta(days=1):
                title = event["title"]
                begin_date = event["start_time"]
                end_date = event["end_time"]
                venue = event["venue"]
                venue_description = event["venue_description"]
                await message.answer(
                    f"""Мероприятие: {title}
                Начало: {begin_date}
                Конец: {end_date}
                Место: {venue}
                Описание: {venue_description}
                Пойдешь?""",
                    reply_markup=all_keyboards["remove_event"](event["key"]),
                )
    else:
        logger.debug(f"Can't find user with {message.from_user.id} tel id")
    await session.close()


async def show_personal_schedule_all(message: types.Message):
    """Answers all personal schedule

    :param message: Message instance
    :type message: types.Message
    """
    logger.debug(f"In show all personal schedule for guest {message.from_user}")
    await message.answer("Расписание за весь период")
    session = SessionLocal()
    user_speech_repo = UserSpeechRepository(session)
    user_repo = UserRepository(session)
    user = await user_repo.get_one(tg_chat_id=message.from_user.id)
    if user:
        user_speech_list = await user_speech_repo.get_all(user["uid"], role="0")
        for user_speech in user_speech_list:
            speech_repo = SpeechRepository(session=session)
            event = await speech_repo.get_one(key=user_speech["key"])
            title = event["title"]
            begin_date = event["start_time"]
            end_date = event["end_time"]
            venue = event["venue"]
            venue_description = event["venue_description"]
            await message.answer(
                f"""Мероприятие: {title}
            Начало: {begin_date}
            Конец: {end_date}
            Место: {venue}
            Описание: {venue_description}
            Пойдешь?""",  # reply_markup=all_keyboards["remove_event"](event["key"]),
            )
    else:
        logger.debug(f"Can't find user with {message.from_user.id} tel id")
    await session.close()


async def show_personal_speech(message: types.Message):
    """Answers personal speech schedule

    :param message: Message instance
    :type message: types.Message
    """
    logger.debug(f"In show personal speech schedule for guest {message.from_user}")
    await message.answer("Мои выступления")
    session = SessionLocal()
    user_speech_repo = UserSpeechRepository(session)
    user_repo = UserRepository(session)
    user = await user_repo.get_one(tg_chat_id=message.from_user.id)
    if user:
        user_speech_list = await user_speech_repo.get_all(user["uid"], role="1")
        for user_speech in user_speech_list:
            speech_repo = SpeechRepository(session=session)
            event = await speech_repo.get_one(key=user_speech["key"])
            title = event["title"]
            begin_date = event["start_time"]
            end_date = event["end_time"]
            venue = event["venue"]
            venue_description = event["venue_description"]
            await message.answer(
                f"""Мероприятие: {title}
            Начало: {begin_date}
            Конец: {end_date}
            Место: {venue}
            Описание: {venue_description}
            Пойдешь?""",  # reply_markup=all_keyboards["remove_speaker"](event["key"]),
            )
    else:
        logger.debug(f"Can't find user with {message.from_user.id} tel id")
    await session.close()


async def return_main_menu(message: types.Message):
    """Handles request to return main menu

    :param message: Message instance
    :type message: types.Message
    """
    logger.debug(f"In return_main_menu handler for guest {message.from_user}")
    await message.answer("Вот меню", reply_markup=all_keyboards["guest_menu"]())
