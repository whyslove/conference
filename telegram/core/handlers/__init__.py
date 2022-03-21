from aiogram import Dispatcher
from loguru import logger

from . import guest, moderator, start_handler


def setup(dp: Dispatcher):
    """Function for recursivly register dispatchers

    Args:
        dp (Dispatcher)
    """
    logger.debug("Start base handler dispatcher")
    dp.register_message_handler(
        start_handler.commands, commands=["start", "stop", "menu", "help"], state="*"
    )
    dp.register_message_handler(start_handler.check_email, state="need_enter_email")
    guest.setup(dp)
    moderator.setup(dp)
    logger.debug("End base handler dispatcher")
