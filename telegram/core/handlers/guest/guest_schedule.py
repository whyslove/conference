from datetime import datetime, timedelta

from aiogram import types
from click import option
from loguru import logger

from core.utils.messages import SCHEDULE_ENTRY_MESSAGE
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
    await message.answer(
        "Выберите опцию. Для навигации используйте кнопки.",
        reply_markup=all_keyboards["guest_personal_schedule"]()
    )


async def show_personal_schedule_today(message: types.Message):
    """Answers personal schedule for today

    :param message: Message instance
    :type message: types.Message
    """
    session = SessionLocal()
    user_speech_repo = UserSpeechRepository(session)
    user_repo = UserRepository(session)
    speech_repo = SpeechRepository(session=session)

    logger.debug(f"In show personal schedule for today for guest {message.from_user}")
    await message.answer("Расписание на сегодня:")

    user = await user_repo.get_one(tg_chat_id=message.from_user.id)
    if not user:
        await message.answer("Мероприятий на сегодня нет :(")
        logger.debug(f"Can't find user with {message.from_user.id} tel id")
        await session.close()
        return
    user_speech_list = await user_speech_repo.get_all(user["uid"], role="0")
    has_events = False
    for user_speech in user_speech_list:
        event = await speech_repo.get_one(key=user_speech["key"])
        if event["start_time"].date() == datetime.today().date():
            has_events = True
            msg = SCHEDULE_ENTRY_MESSAGE.format(
                title=event["title"],
                starts_at=event["start_time"].strftime("%d-%m %H:%M"),
                ends_at=event["end_time"].strftime("%d-%m %H:%M"),
                venue=event["venue"],
                venue_description=event["venue_description"],
            )
            await message.answer(
                msg,
                # reply_markup=all_keyboards["remove_event"](event["key"]),
                parse_mode='HTML'
            )
    if not has_events:
        logger.debug(f"User {message.from_user.id} has not events for today")
        await message.answer("Мероприятий на сегодня нет :(")

    await session.close()


async def show_personal_schedule_tomorrow(message: types.Message):
    """Answers personal schedule for tomorrow

    :param message: Message instance
    :type message: types.Message
    """
    session = SessionLocal()
    user_speech_repo = UserSpeechRepository(session)
    user_repo = UserRepository(session)
    speech_repo = SpeechRepository(session=session)

    logger.debug(f"In show personal schedule for tomorrow for guest {message.from_user}")
    await message.answer("Расписание на завтра:")

    user = await user_repo.get_one(tg_chat_id=message.from_user.id)
    if not user:
        await message.answer("Мероприятий на завтра нет :(")
        logger.debug(f"Can't find user with {message.from_user.id} tel id")
        await session.close()
        return
    user_speech_list = await user_speech_repo.get_all(user["uid"], role="0")
    has_events = False
    for user_speech in user_speech_list:
        event = await speech_repo.get_one(key=user_speech["key"])
        if event["start_time"].date() == datetime.today().date() + timedelta(days=1):
            has_events = True
            msg = SCHEDULE_ENTRY_MESSAGE.format(
                title=event["title"],
                starts_at=event["start_time"].strftime("%d-%m %H:%M"),
                ends_at=event["end_time"].strftime("%d-%m %H:%M"),
                venue=event["venue"],
                venue_description=event["venue_description"],
            )
            await message.answer(
                msg,
                # reply_markup=all_keyboards["remove_event"](event["key"]),
                parse_mode='HTML',
            )
    if not has_events:
        logger.debug(f"User {message.from_user.id} has not events for tomorrow")
        await message.answer("Мероприятий на завтра нет :(")

    await session.close()


async def show_personal_schedule_all(message: types.Message):
    """Answers all personal schedule

    :param message: Message instance
    :type message: types.Message
    """
    session = SessionLocal()
    user_speech_repo = UserSpeechRepository(session)
    user_repo = UserRepository(session)
    speech_repo = SpeechRepository(session=session)

    logger.debug(f"In show all personal schedule for guest {message.from_user}")
    await message.answer("Расписание за весь период:")

    user = await user_repo.get_one(tg_chat_id=message.from_user.id)
    if not user:
        await message.answer("Мероприятий нет :(")
        logger.debug(f"Can't find user with {message.from_user.id} tel id")
        await session.close()
    user_speech_list = await user_speech_repo.get_all(user["uid"], role="0")
    has_events = False
    for user_speech in user_speech_list:
        event = await speech_repo.get_one(key=user_speech["key"])
        has_events = True
        msg = SCHEDULE_ENTRY_MESSAGE.format(
            title=event["title"],
            starts_at=event["start_time"].strftime("%d-%m %H:%M"),
            ends_at=event["end_time"].strftime("%d-%m %H:%M"),
            venue=event["venue"],
            venue_description=event["venue_description"],
        )
        await message.answer(
            msg,
            # reply_markup=all_keyboards["remove_event"](event["key"]),
            parse_mode='HTML'
        )
    if not has_events:
        logger.debug(f"User {message.from_user.id} has not events")
        await message.answer("Мероприятий нет :(")
    await session.close()


async def show_personal_speech(message: types.Message):
    """Answers personal speech schedule

    :param message: Message instance
    :type message: types.Message
    """
    session = SessionLocal()
    user_speech_repo = UserSpeechRepository(session)
    user_repo = UserRepository(session)
    speech_repo = SpeechRepository(session=session)

    logger.debug(f"In show personal speech schedule for guest {message.from_user}")
    await message.answer("Ваши выступления:")

    user = await user_repo.get_one(tg_chat_id=message.from_user.id)
    if not user:
        await message.answer("Мероприятий, где вы спикер, нет :(")
        logger.debug(f"Can't find user with {message.from_user.id} tel id")
        await session.close()
        return
    user_speech_list = await user_speech_repo.get_all(user["uid"], role="1")
    has_events = False
    for user_speech in user_speech_list:
        event = await speech_repo.get_one(key=user_speech["key"])
        has_events = True
        msg = SCHEDULE_ENTRY_MESSAGE.format(
            title=event["title"],
            starts_at=event["start_time"].strftime("%d-%m %H:%M"),
            ends_at=event["end_time"].strftime("%d-%m %H:%M"),
            venue=event["venue"],
            venue_description=event["venue_description"],
        )
        await message.answer(
            msg,
            # reply_markup=all_keyboards["remove_event"](event["key"]),
            parse_mode='HTML'
        )
    if not has_events:
        await message.answer("Мероприятий, где вы спикер, нет :(")
    await session.close()


async def return_main_menu(message: types.Message):
    """Handles request to return main menu

    :param message: Message instance
    :type message: types.Message
    """
    logger.debug(f"In return_main_menu handler for guest {message.from_user}")
    await message.answer(
        "Вот меню. Для навигации используйте кнопки!", reply_markup=all_keyboards["guest_menu"]()
    )
