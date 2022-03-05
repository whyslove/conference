"""Module to declare guest filters."""
import re
from loguru import logger
from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class CallBackFilter(BoundFilter):
    """Class to filter callbacks."""

    key = "callback_status"

    def __init__(self, status):
        self.status = status
        logger.debug(f"Callback initialization")

    async def check(self, callback: types.CallbackQuery) -> bool:
        """Checks whether status of the event is right.

        :param call: Callback instance
        :type call: types.CallbackQuery
        :return: whether status of the event is right
        :rtype: str
        """
        logger.debug(f"Full callback name: {callback.data}")
        callback_status = re.findall("[a-zA-Z]+", callback.data)[0]
        logger.debug(f"{callback_status}")
        return callback_status == self.status
