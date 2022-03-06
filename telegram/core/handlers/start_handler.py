from cgitb import text
import aiohttp

from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from loguru import logger
from core.config import config
from core.keyboards.all_keyboards import all_keyboards
from core.database.repositories import token, user
from core.database.create_table import SessionLocal
from core.database.repositories import token


async def ask_email(message: types.Message, state: FSMContext):
    await message.answer("Введите email")
    await state.set_state("need_enter_email")


async def check_email(message: types.Message, state: FSMContext):
    """Asks email and if email exist assign special state according to its role. Then updates db with tg_chat_id"""

    logger.info(f"Receive message from tg {message.text}")
    ur = user.UserRepository(session=SessionLocal())
    # TODO send email on email to condirm identity
    user_ = await ur.get_one(uid=str.lower(message.text))
    if not user_:
        logger.info(f"unknown email f{message.text}")
        await message.answer("неправильный email, введите его ещё раз")
        return
    if user_["is_admin"]:
        role = "moderator"
    else:
        role = "guest"
    await ur.update(uid=str.lower(message.text), new_tg_chat_id=message.from_user.id)
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
            logger.info(f"unknown role f{message.text}")
            await message.answer("неправильный email, введите его ещё раз")
