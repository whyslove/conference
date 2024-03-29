from ast import fix_missing_locations
from tkinter.tix import Tree
from pydantic import SecretStr
from loguru import logger
from aiogram import types
from aiogram.dispatcher.storage import FSMContext

from core.database.create_table import SessionLocal
from core.database.repositories.speech import SpeechRepository
from core.utils.reminder import ModeratorReminder, SpeakerReminder
from core import config
from core.utils.utils import clear_directory, reset_base_state
from core.utils.parser_csv import parse_xlsx, delete_all_data_in_tables
from core.keyboards.all_keyboards import all_keyboards
from core.database.repositories.user_speech import UserSpeechRepository


async def prepare_upload_xls(message: types.Message, state: FSMContext):
    """Set appropriate state"""
    logger.debug("Prepare upload xls")
    await state.set_state("ready_upload_xls")
    await message.answer("Загрузите сюда файл .xls", reply_markup=all_keyboards["back_button"]())


async def upload_xls(message: types.Message, state: FSMContext):
    logger.debug("Upload csv")
    if message.text == "Вернуться назад":
        await reset_base_state(message, state)
        await message.answer("Вы вернулись назад")
        return
    elif message.text == "Удалить все данные":
        await delete_all_data_in_tables()
        await message.answer("Вы удалили все данные из таблиц")
        return

    file_id = message.document.file_id
    dest_dir = "./root_xlsx"
    file_name = "xlsx_file.xlsx"

    clear_directory(dest_dir)  # to prevent from multiple files
    dest = await message.bot.download_file_by_id(
        file_id=file_id, destination="./root_xlsx/xlsx_file.xlsx", make_dirs=True
    )
    if dest:  # ????????????????????? ваще хз чо будет здесь елси всё крашнется
        await message.answer("Подождите пожалуйста, это может занять некоторое время")
        error = await parse_xlsx(dest_dir + "/" + file_name, message.from_user.id)
        if error == None:
            await message.answer("Файл успешно загружен")
            await reset_base_state(message, state)
            # set reminder to moderator
            logger.debug(f"Setting reminds for moderator {message.from_user}")
            session = SessionLocal()
            speech_repo = SpeechRepository(session)
            event_list = await speech_repo.get_all()
            if event_list:
                for event in event_list:
                    reminder = ModeratorReminder(event)
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
