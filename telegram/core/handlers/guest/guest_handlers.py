from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from loguru import logger


async def general_schedule(message: types.Message, state: FSMContext):
    """

    :param message: Message instance
    :type message: types.Message
    :param state: FSMContext instance
    :type state: FSMContext
    """
    logger.debug("In general schedule for guest")
    await message.answer("From function in general schedule")
