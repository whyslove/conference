"Module to declare speakers responses."

from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from loguru import logger
from core.database.create_table import SessionLocal
from core.database.repositories.speech import SpeechRepository
from core.database.repositories.user_speech import UserSpeechRepository
from core.database.repositories.user import UserRepository


async def show_responses(message: types.Message, state: FSMContext):
    """

    :param message: Message instance
    :type message: types.Message
    :param state: FSMContext instance
    :type state: FSMContext
    """
    session = SessionLocal()
    user_speech_repo = UserSpeechRepository(session)
    speech_repo = SpeechRepository(session)
    user_repo = UserRepository(session)

    logger.debug(f"In show responses for moderator {message.from_user}")

    user_speech_list = await user_speech_repo.get_all()
    sorted(
        user_speech_list,
        key=lambda user_speech: (user_speech["key"], user_speech["role"], user_speech["uid"]),
    )
    await message.answer("Текущие ответы участников:")
    for user_speech in user_speech_list:
        user = await user_repo.get_one(uid=user_speech["uid"])
        event = await speech_repo.get_one(key=user_speech["key"])
        acknowledgment = user_speech["acknowledgment"]
        if acknowledgment:
            await message.answer(
                f"{user['snp']}: {'спикер' if user_speech['role'] == '1' else 'гость'} написал: \"{acknowledgment}\" о мероприятии <b>\"{event['title']}\"</b>",
                parse_mode="HTML",
            )
        else:
            await message.answer(
                f"{user['snp']}: {'спикер' if user_speech['role'] == '1' else 'гость'} ничего не написал о мероприятии <b>\"{event['title']}\"</b>",
                parse_mode="HTML",
            )
