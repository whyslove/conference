from ast import fix_missing_locations
from tkinter.tix import Tree
from pydantic import SecretStr
from core.database.repositories import token, user
from core.database.create_table import SessionLocal
from core.database.repositories.speech import SpeechRepository
from core.utils.reminder import ModeratorReminder
from core import config
from loguru import logger
from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from core.utils.utils import clear_directory
from core.utils.parser_csv import parse_xlsx


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
        await state.reset_state()


async def enter_email_for_token(message: types.Message, state: FSMContext):
    logger.debug(f"Get email, {message.text}, try update")
    ur = user.UserRepository(session=SessionLocal())
    if ur.get_one(uid=message.text):
        await ur.update(uid=message.text, new_is_admin=True)
        await message.answer("Вы стали модератором")
        await state.set_state("moderator_main")
    else:
        await message.answer("Такая почта не найдена")
        await state.reset_state()


async def prepare_upload_xls(message: types.Message, state: FSMContext):
    logger.debug("Prepare upload xls")
    await state.set_state("ready_upload_xls")
    await message.answer("Загрузите сюда файл .xls")


async def upload_xls(message: types.Message, state: FSMContext):
    logger.debug("Upload csv")
    file_id = message.document.file_id
    dest_dir = "./root_xlsx"
    file_name = "xlsx_file.xlsx"

    clear_directory(dest_dir)  # to prevent from multiple files
    dest = await message.bot.download_file_by_id(
        file_id=file_id, destination="./root_xlsx/xlsx_file.xlsx", make_dirs=True
    )
    if dest:  # ????????????????????? ваще хз чо будет здесь елси всё крашнется
        await message.answer("Подождите пожалуйста, это может занять некоторое время")
        error = await parse_xlsx(dest_dir + "/" + file_name)
        if error == None:
            await message.answer("Файл успешно загружен")
            # set reminder to moderator
            logger.debug(f"Setting reminds for moderator {message.from_user}")
            session = SessionLocal()
            speech_repo = SpeechRepository(session)
            for event in await speech_repo.get_all():
                reminder = ModeratorReminder(message.from_user.id, event)
                config.sc.add_remind(reminder)
            logger.debug(f"Reminds for moderator {message.from_user} set successfully")
        else:
            await message.answer(error)
            return
    else:
        await message.answer("Ошибка при загрузке, свяжитесь с раззработчиками")
        logger.error("Error while dowloading file from tg")

    await state.set_state("moderator_main")
