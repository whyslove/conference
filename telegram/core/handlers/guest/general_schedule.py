from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from loguru import logger

from core.utils.messages import SCHEDULE_ENTRY_MESSAGE
from core.keyboards.all_keyboards import all_keyboards
from core.database.create_table import SessionLocal
from core.database.repositories.speech import SpeechRepository
from core.database.repositories.user_speech import UserSpeechRepository
from core.database.repositories.user import UserRepository


async def general_schedule(message: types.Message, state: FSMContext):
    session = SessionLocal()
    user_speech_repo = UserSpeechRepository(session)
    user_repo = UserRepository(session)
    speech_repo = SpeechRepository(session)

    logger.debug("In general schedule for guest")
    await message.answer("Общее расписание:")

    # Forming list where user is guest already
    user = await user_repo.get_one(tg_chat_id=message.from_user.id)
    if not user:
        await message.answer("Мероприятий нет :(")
        logger.debug(f"Can't find user with {message.from_user.id} tel id")
        await session.close()
        return
    user_speech_list = await user_speech_repo.get_all(user["uid"])
    previous_selected_list = [user_speech["key"] for user_speech in user_speech_list]
    has_events = False
    for event in await speech_repo.get_all():
        has_events = True
        selected = event["key"] in previous_selected_list
        msg_text = SCHEDULE_ENTRY_MESSAGE.format(
            title=event["title"],
            starts_at=event["start_time"].strftime("%d-%m %H:%M"),
            ends_at=event["end_time"].strftime("%d-%m %H:%M"),
            venue=event["venue"],
            venue_description=event["venue_description"],
        )
        if selected:
            msg_text += "\n<em>Вы записаны на это мероприятие</em>"
        await message.answer(
            msg_text,
            reply_markup=all_keyboards["add_event"](event["key"]) if not selected else None,
            parse_mode="HTML",
        )
    if not has_events:
        await message.answer("Мероприятий нет :(")
    await session.close()
