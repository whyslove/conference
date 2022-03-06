from cgitb import text
from aiogram import Dispatcher
from loguru import logger
from . import moderator_handlers
import re


def setup(dp: Dispatcher):
    """Function for recursivly register dispatchers

    Args:
        dp (Dispatcher)
    """
    logger.debug("Start moderator handler dispatcher")
    dp.register_message_handler(
        moderator_handlers.start_enter_token,
        regexp=re.compile("ввести токен", re.IGNORECASE),
        state="*",
    )
    dp.register_message_handler(moderator_handlers.use_token, state="enter_token")
    dp.register_message_handler(moderator_handlers.start_enter_token, state="enter_email")
    dp.register_message_handler(
        moderator_handlers.enter_email_for_token, state="enter_email_for_token"
    )
    dp.register_message_handler(
        moderator_handlers.prepare_upload_xls, text="Загрузить расписание", state="moderator_main"
    )
    dp.register_message_handler(
        moderator_handlers.upload_xls, state="ready_upload_xls", content_types=["document"]
    )
    logger.debug("End moderator handler dispatcher")
