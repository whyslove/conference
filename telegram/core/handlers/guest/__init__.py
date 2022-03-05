from .guest_handlers import general_schedule
from .guest_schedule import (
    personal_schedule,
    show_personal_schedule_today,
    show_personal_schedule_tomorrow,
    show_personal_schedule_all,
    return_main_menu,
    show_personal_speech,
)
from .event_status import add_event, remove_event
from core.filters.guest_filters import CallBackFilter
from aiogram import Dispatcher


def setup(dp: Dispatcher):
    """Function for recusivevly register dispatchers"""
    dp.register_message_handler(general_schedule, regexp="Общее расписание", state="guest_main")
    dp.register_message_handler(personal_schedule, regexp="Моё раcписание", state="guest_main")
    dp.register_message_handler(
        show_personal_schedule_today, regexp="Сегодня", state="guest_main"
    )
    dp.register_message_handler(
        show_personal_schedule_tomorrow, regexp="Завтра", state="guest_main"
    )
    dp.register_message_handler(
        show_personal_schedule_all, regexp="Весь период", state="guest_main"
    )
    dp.register_message_handler(show_personal_speech, regexp="Выступления", state="guest_main")
    dp.register_message_handler(
        return_main_menu, regexp="Вернуться в главное меню", state="guest_main"
    )
    dp.register_callback_query_handler(add_event, CallBackFilter("add"), state="guest_main")
    dp.register_callback_query_handler(
        remove_event, CallBackFilter("removeEvent"), state="guest_main"
    )

