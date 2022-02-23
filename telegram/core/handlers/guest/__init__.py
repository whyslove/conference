from .guest_handlers import general_schedule
from aiogram import Dispatcher


def setup(dp: Dispatcher):
    """Function for recusivevly register dispatchers"""
    dp.register_message_handler(general_schedule, regexp="Общее расписание", state="guest_main")
