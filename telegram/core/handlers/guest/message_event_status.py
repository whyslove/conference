"""Module to declare message handlers to handle text response about event status."""
from aiogram import types
from loguru import logger
from aiogram.dispatcher.storage import FSMContext
from core.database.create_table import SessionLocal
from core import config
from core.database.repositories.user_speech import UserSpeechRepository
from core.utils.reminder import SpeakerReminder
from core.database.repositories.user_speech import UserSpeechRepository
from core.database.repositories.user import UserRepository


async def event_status_guest(message: types.Message, state: FSMContext):
    """Handles result whether guest will go to a speech or not

    :param message: Message instance
    :type message: types.Message
    :param state: FSMContext instance
    :type state: FSMContext:
    """
    session = SessionLocal()
    user_repo = UserRepository(session)
    user = await user_repo.get_one(tg_chat_id=message.from_user.id)
    user_speech_repo = UserSpeechRepository(session)
    event_data = await state.get_data()
    print(event_data)
    match message.text.lower():
        case "пойду":
            await user_speech_repo.update(
                uid=user["uid"], key=event_data["key"], new_acknowledgment=message.text
            )
            await message.answer("Отлично")
            await state.reset_data()
            await state.set_state("guest_main")
        case "не пойду":
            await user_speech_repo.update(
                uid=user["uid"], key=event_data["key"], new_acknowledgment=message.text
            )
            await message.answer("Жаль")
            await state.set_state("guest_main")
        case _:
            await message.answer("Не могу разобрать, напиши Пойду или Не пойду")


async def event_status_speaker(message: types.Message, state: FSMContext):
    """Handles result whether speaker will go to a speech or not

    :param message: Message instance
    :type message: types.Message
    :param state: FSMContext instance
    :type state: FSMContext:
    """
    session = SessionLocal()
    user_repo = UserRepository(session)
    user = await user_repo.get_one(tg_chat_id=message.from_user.id)
    moderator = await user_repo.get_one(is_admin=True)
    user_speech_repo = UserSpeechRepository(session)
    event_data = await state.get_data()
    if moderator:
        # send data to moderator
        if moderator["tg_chat_id"]:
            await message.bot.send_message(moderator["tg_chat_id"], message.text)
        else:
            logger.debug("No tg_chat_id for moderator")
    else:
        logger.debug("No moderators")
    if message.text.lower() == "не пойду":
        speaker_reminder = SpeakerReminder(chat_id=message.from_user.id, event=event_data)
        config.sc.remove_remind(speaker_reminder)
        message.answer("Жаль")
    else:
        await message.answer("Отлично")
    # update information
    await user_speech_repo.update(
        uid=user["uid"], key=event_data["key"], new_acknowledgment=message.text
    )
    await state.reset_data()
    await state.set_state("guest_main")