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
    logger.debug(f"In show responses for moderator {message.from_user}")
    session = SessionLocal()
    user_speech_repo = UserSpeechRepository(session)
    user_speech_list = await user_speech_repo.get_all()
    speech_repo = SpeechRepository(session)
    for user_speech in user_speech_list:
        user_repo = UserRepository(session)
        user = await user_repo.get_one(uid=user_speech["uid"])
        acknowledgment = user_speech["acknowledgment"]
        event = await speech_repo.get_one(key=user_speech["key"])
        acknowledgment = user_speech["acknowledgment"]
        if acknowledgment:
            await message.answer(
                f"{user['snp']} написал: \"{acknowledgment}\" о мероприятии \"{event['title']}\""
            )
        else:
            await message.answer(
                f"{user['snp']} ничего не написал о мероприятии \"{event['title']}\""
            )
