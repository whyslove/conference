from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from loguru import logger

from core.utils.messages import SCHEDULE_ENTRY_MESSAGE
from core.database.create_table import SessionLocal
from core.database.repositories.speech import SpeechRepository

from core.keyboards.all_keyboards import all_keyboards


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
    has_events = False
    for event in await speech_repo.get_all():
        has_events = True
        msg = SCHEDULE_ENTRY_MESSAGE.format(
            title=event["title"],
            starts_at=event["start_time"].strftime("%d-%m %H:%M"),
            ends_at=event["end_time"].strftime("%d-%m %H:%M"),
            venue=event["venue"],
        )
        await message.answer(msg, parse_mode='HTML', reply_markup=all_keyboards['show_desc'](event['key']))
    if not has_events:
        await message.answer("Мероприятий нет :(")
    await session.close()
