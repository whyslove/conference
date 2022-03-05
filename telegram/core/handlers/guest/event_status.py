"""Module to declare event status handler."""
import re
from aiogram import types
from loguru import logger
from core.keyboards.all_keyboards import all_keyboards


async def add_event(callback: types.CallbackQuery):
    """Adds event to personal schedule and make a job for reminder

    :param callback: Callback instance
    :type callback: types.CallbackQuery
    """
    event_id = re.findall("\d+", callback.data)[0]
    logger.debug(f"Guest {callback.from_user} chose to add {event_id}")
    # TODO check added before
    # TODO check intersections
    # TODO insert line in USER_SPEACH
    # Create a job to make a notification
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(callback.message.text + "\nВы выбрали это мероприятие")


async def remove_event(callback: types.CallbackQuery):
    """Removes event to personal schedule and delete a job for reminder

    :param callback: Callback instance
    :type callback: types.CallbackQuery
    """
    event_id = re.findall("\d+", callback.data)[0]
    logger.debug(f"Guest {callback.from_user} chose to remove {event_id}")
    # TODO check removed before
    # TODO delete line in USER_SPEACH
    # delete a job to make a notification
    await callback.message.delete()
