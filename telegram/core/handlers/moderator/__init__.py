from cgitb import text
from aiogram import Dispatcher
from loguru import logger
from . import moderator_handlers
from .general_schedule import general_schedule
from .show_responses import show_responses
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
    dp.register_message_handler(general_schedule, regexp="Общее расписание", state="moderator_main")
    dp.register_message_handler(show_responses, regexp="Ответы участников", state="moderator_main")
    logger.debug("End moderator handler dispatcher")
