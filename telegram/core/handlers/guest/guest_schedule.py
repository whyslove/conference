"""Module to illustrate personal schedule."""

from aiogram import types
from click import option
from loguru import logger
from core.keyboards.all_keyboards import all_keyboards


async def personal_schedule(message: types.Message):
    """Choosing personal schedule

    :param message: Message instance
    :type message: types.Message
    """
    logger.debug(f"In personal schedule for guest {message.from_user}")
    await message.answer("Выберите опцию", reply_markup=all_keyboards["guest_personal_schedule"]())


async def show_personal_schedule_today(message: types.Message):
    """Answers personal schedule for today

    :param message: Message instance
    :type message: types.Message
    """
    logger.debug(f"In show personal schedule for today for guest {message.from_user}")
    await message.answer("Расписание на сегодня")
    # TODO get personal schedule and answer with delay
    event_name = "Python0"
    begin_date = "01.01.2020 13:00"
    end_date = "01.01.2020 14:00"
    field = "МЕМ"
    description = "Оч крутое мероприятие"
    await message.answer(
        f"""Мероприятие: {event_name}
    Начало: {begin_date}
    Конец: {end_date}
    Место: {field}
    Описание: {description}
    Пойдешь?""",
        reply_markup=all_keyboards["remove_event"]("1315"),
    )


async def show_personal_schedule_tomorrow(message: types.Message):
    """Answers personal schedule for tomorrow

    :param message: Message instance
    :type message: types.Message
    """
    logger.debug(f"In show personal schedule for tomorrow for guest {message.from_user}")
    await message.answer("Расписание на завтра")
    # TODO get personal schedule and answer with delay
    event_name = "Python1"
    begin_date = "01.01.2020 13:00"
    end_date = "01.01.2020 14:00"
    field = "МЕМ"
    description = "Оч крутое мероприятие"
    await message.answer(
        f"""Мероприятие: {event_name}
    Начало: {begin_date}
    Конец: {end_date}
    Место: {field}
    Описание: {description}
    Пойдешь?""",
        reply_markup=all_keyboards["remove_event"]("1315"),
    )


async def show_personal_schedule_all(message: types.Message):
    """Answers all personal schedule

    :param message: Message instance
    :type message: types.Message
    """
    logger.debug(f"In show all personal schedule for guest {message.from_user}")
    await message.answer("Расписание за весь период")
    # TODO get personal schedule and answer with delay
    event_name = "Python3"
    begin_date = "01.01.2020 13:00"
    end_date = "01.01.2020 14:00"
    field = "МЕМ"
    description = "Оч крутое мероприятие"
    await message.answer(
        f"""Мероприятие: {event_name}
    Начало: {begin_date}
    Конец: {end_date}
    Место: {field}
    Описание: {description}
    Пойдешь?""",
        reply_markup=all_keyboards["remove_event"]("1315"),
    )


async def show_personal_speech(message: types.Message):
    """Answers personal speech schedule

    :param message: Message instance
    :type message: types.Message
    """
    logger.debug(f"In show personal speech schedule for guest {message.from_user}")
    # TODO get personal schedule for speech and answer with delay
    await message.answer("Мои выступления")
    # TODO get personal schedule and answer with delay
    event_name = "PythonSpeech"
    begin_date = "01.01.2020 13:00"
    end_date = "01.01.2020 14:00"
    field = "МЕМ"
    description = "Оч крутое мероприятие"
    await message.answer(
        f"""Мероприятие: {event_name}
    Начало: {begin_date}
    Конец: {end_date}
    Место: {field}
    Описание: {description}
    Пойдешь?""",
        reply_markup=all_keyboards["remove_speech"]("1315"),
    )


async def return_main_menu(message: types.Message):
    """Handles request to return main menu

    :param message: Message instance
    :type message: types.Message
    """
    logger.debug(f"In return_main_menu handler for guest {message.from_user}")
    await message.answer("Вот меню", reply_markup=all_keyboards["guest_menu"]())
