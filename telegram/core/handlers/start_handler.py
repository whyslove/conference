from cgitb import text
import aiohttp

from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from loguru import logger
from core.config import config
from core.keyboards.all_keyboards import all_keyboards

from core.database.repositories import token


async def ask_email(message: types.Message, state: FSMContext):
    """

    :param message: Message instance
    :type message: types.Message
    :param state: FSMContext instance
    :type state: FSMContext
    """
    logger.info(f"Receive message from tg {message}")
    logger.debug(f"Searching email {message.text} in db")
    # FIXME add db check
    # TODO send email on email to condirm identity
    # role = anser.from.db(email)
    role = "moderator"
    match role:
        case "moderator":
            logger.debug("Finally it is moderator")
            await state.set_state("moderator_main")
            await message.answer("Вот меню", reply_markup=all_keyboards["moderator_menu"]())
        case "guest":
            logger.debug("Finally it is guest")
            await state.set_state("guest_main")
            await message.answer("Вот меню", reply_markup=all_keyboards["guest_menu"]())

        case _:
            logger.info(f"Unknown email f{message.text}")
            await message.answer("Неправильный email, введите его ещё раз")
