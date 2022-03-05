from aiogram import Dispatcher
from loguru import logger

from . import guest, moderator, start_handler


def setup(dp: Dispatcher):
    """Function for recursivly register dispatchers

    Args:
        dp (Dispatcher)
    """
    logger.debug("Start base handler dispatcher")
    guest.setup(dp)
    moderator.setup(dp)
    dp.register_message_handler(start_handler.ask_email, commands="start")
    logger.debug("End base handler dispatcher")
