from ast import fix_missing_locations
from pydantic import SecretStr
from core.database.repositories import token, user
from core.database.create_table import SessionLocal
from loguru import logger
from aiogram import types
from aiogram.dispatcher.storage import FSMContext


async def start_enter_token(message: types.Message, state: FSMContext):
    logger.debug(f"User want to upgrade to admin")
    await state.set_state("enter_token")
    await message.answer("Введите токен")


async def use_token(message: types.Message, state: FSMContext):
    logger.debug(f"Get token, start check it")
    logger.debug(f"Token {message.text}")
    tr = token.TokenRepository(session=SessionLocal())

    if await tr.get_one(token=message.text):
        await state.set_state("enter_email")
        await message.answer("Теперь введите вашу почту")
    else:
        await message.answer("Неправильный токен")
        await state.finish()


async def enter_email_for_token(message: types.Message, state: FSMContext):
    logger.debug(f"Get email, {message.text}, try update")
    ur = user.UserRepository(session=SessionLocal())
    if ur.get_one(uid=message.text):
        await ur.update(uid=message.text, new_is_admin=True)
        await message.answer("Вы стали модератором")
        await state.set_state("moderator_main")
    else:
        await message.answer("Такая почта не найдена")
        await state.finish()


async def prepare_upload_csv(message: types.Message, state: FSMContext):
    logger.debug("Prepare upload csv")
    await message.answer("Загрузите сюда файл .xls")
    await state.set_state("ready_upload_csv")


async def upload_csv(message: types.Message, state: FSMContext):
    logger.debug("Upload csv")
