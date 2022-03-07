from ast import fix_missing_locations
from tkinter.tix import Tree
from pydantic import SecretStr
from core.database.repositories import token, user
from core.database.create_table import SessionLocal
from core.database.repositories.speech import SpeechRepository
from core.utils.reminder import ModeratorReminder, SpeakerReminder
from core import config
from loguru import logger
from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from core.utils.utils import clear_directory
from core.utils.parser_csv import parse_xlsx
from core.keyboards.all_keyboards import all_keyboards
from core.database.repositories.user_speech import UserSpeechRepository


async def start_enter_token(message: types.Message, state: FSMContext):
    logger.debug(f"User want to upgrade to admin")
    await state.set_state("enter_token")
    await message.answer("Введите токен")


async def use_token(message: types.Message, state: FSMContext):
    logger.debug(f"Get token, start check it")
    logger.debug(f"Token {message.text}")
    tr = token.TokenRepository(session=SessionLocal())

    if await tr.get_one(token=message.text, vacant=True):
        await state.set_state("enter_email_for_token")
        # await tr.update(token=message.text, new_vacant=False)
        await message.answer("Теперь введите вашу почту")
    else:
        await message.answer("Неправильный токен")
        await state.reset_state()
    tr.session.close()


async def enter_email_for_token(message: types.Message, state: FSMContext):
    logger.debug(f"Get email, {message.text}, try update")
    ur = user.UserRepository(session=SessionLocal())
    if await ur.get_one(uid=message.text):  # if it existing user
        ur.update(uid=message.text, new_is_admin=True)
    else:  # if db is empty and it is false user
        await ur.add(
            {
                "uid": message.text,
                "is_admin": True,
                "snp": "",
                "phone": "",
                "tg_chat_id": message.from_user.id,
            }
        )
    await message.answer("Вы стали модератором")
    await state.set_state("moderator_main")
    await message.answer("Вот меню", reply_markup=all_keyboards["moderator_menu"]())

    ur.session.close()


async def prepare_upload_xls(message: types.Message, state: FSMContext):
    """Set appropriate state"""

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
            event_list = await speech_repo.get_all()
            if event_list:
                for event in event_list:
                    reminder = ModeratorReminder(message.from_user.id, event)
                    config.sc.add_remind(reminder)
                logger.debug(f"Reminds for moderator {message.from_user} set successfully")
            else:
                logger.debug(f"Reminds for moderator {message.from_user} don't set")
            logger.debug(f"Setting reminds for speakers {message.from_user}")
            user_speech_repo = UserSpeechRepository(session)
            user_speech_list = await user_speech_repo.get_all(role="1")
            if user_speech_list:
                for user_speech in user_speech_list:
                    event = await speech_repo.get_one(key=user_speech["key"])
                    speaker_reminder = SpeakerReminder(user_speech["uid"], event)
                    config.sc.add_remind(speaker_reminder)
                logger.debug(f"Reminds for speaker {message.from_user} set successfully")
            else:
                logger.debug(f"Reminds for speaker {message.from_user} don't set")
        else:
            await message.answer(error)
            return
    else:
        await message.answer("Ошибка при загрузке, свяжитесь с раззработчиками")
        logger.error("Error while dowloading file from tg")

    await state.set_state("moderator_main")
