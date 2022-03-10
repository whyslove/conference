from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from loguru import logger
from core.database.create_table import SessionLocal
from core.database.repositories.speech import SpeechRepository


async def general_schedule(message: types.Message, state: FSMContext):
    """

    :param message: Message instance
    :type message: types.Message
    :param state: FSMContext instance
    :type state: FSMContext
    """
    logger.debug(f"In general schedule for moderator {message.from_user}")
    await message.answer("Общее расписание:")
    session = SessionLocal()
    speech_repo = SpeechRepository(session)
    has_event = False
    for event in await speech_repo.get_all():
        has_event = True
        title = event["title"]
        begin_date = event["start_time"]
        end_date = event["end_time"]
        venue = event["venue"]
        venue_description = event["venue_description"]
        await message.answer(
            f"""Мероприятие: \"{title}\"
    Начало: {begin_date.strftime("%d-%m %H:%M")}
    Конец: {end_date.strftime("%d-%m %H:%M")}
    Место: {venue}
    Описание: {venue_description}""",
        )
    if not has_event:
        await message.answer("Мероприятий нет :(")
    await session.close()
