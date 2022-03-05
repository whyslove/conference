"""Package to declare filters."""
from aiogram import Dispatcher
from loguru import logger
from . import guest_filters


def setup(dp: Dispatcher):
    """Setups filters.

    :param dp: Dispatcher instance
    :type dp: Dispatcher
    """
    logger.debug("Set up of filters...")
    dp.filters_factory.bind(guest_filters.CallBackFilter)
    logger.debug("Successful")
