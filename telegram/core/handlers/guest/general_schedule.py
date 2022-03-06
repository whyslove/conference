from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from loguru import logger
from core.keyboards.all_keyboards import all_keyboards
from core.database.create_table import SessionLocal
from core.database.repositories.speech import SpeechRepository
from core.database.repositories.user_speech import UserSpeechRepository
from core.database.repositories.user import UserRepository


async def general_schedule(message: types.Message, state: FSMContext):
    """

    :param message: Message instance
    :type message: types.Message
    :param state: FSMContext instance
    :type state: FSMContext
    """
    logger.debug("In general schedule for guest")
    await message.answer("Общее расписание:")
    # Forming list where user is guest already
    session = SessionLocal()
    user_speech_repo = UserSpeechRepository(session)
    user_repo = UserRepository(session)
    user = await user_repo.get_one(tg_chat_id=message.from_user.id)
    if user:
        user_speech_list = await user_speech_repo.get_all(user["uid"])
        previous_selected_list = [user_speech["key"] for user_speech in user_speech_list]
        speech_repo = SpeechRepository(session)
        for event in await speech_repo.get_all():
            title = event["title"]
            begin_date = event["start_time"]
            end_date = event["end_time"]
            venue = event["venue"]
            venue_description = event["venue_description"]
            selected = event["key"] in previous_selected_list
            if not selected:
                await message.answer(
                    f"""Мероприятие: {title}
            Начало: {begin_date}
            Конец: {end_date}
            Место: {venue}
            Описание: {venue_description}""",
                    reply_markup=all_keyboards["add_event"](event["key"]),
                )
            else:
                await message.answer(
                    f"""Мероприятие: {title}
        Начало: {begin_date}
        Конец: {end_date}
        Место: {venue}
        Описание: {venue_description}
        Вы ранее записались на это мероприятие""",
                )
    else:
        logger.debug(f"Can't find user with {message.from_user.id} tel id")
    await session.close()
