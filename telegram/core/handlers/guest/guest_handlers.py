from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from loguru import logger
from core.keyboards.all_keyboards import all_keyboards


async def general_schedule(message: types.Message, state: FSMContext):
    """

    :param message: Message instance
    :type message: types.Message
    :param state: FSMContext instance
    :type state: FSMContext
    """
    logger.debug("In general schedule for guest")
    await message.answer("Общее расписание:")
    # TODO get general schedule and answer with delay
    event_name = "Python"
    begin_date = "01.01.2020 13:00"
    end_date = "01.01.2020 14:00"
    field = "МЕМ"
    description = "Оч крутое мероприятие"
    selected = False
    if not selected:
        await message.answer(
            f"""Мероприятие: {event_name}
    Начало: {begin_date}
    Конец: {end_date}
    Место: {field}
    Описание: {description}""",
            reply_markup=all_keyboards["add_event"]("1315"),
        )
    else:
        await message.answer(
            f"""Мероприятие: {event_name}
Начало: {begin_date}
Конец: {end_date}
Место: {field}
Описание: {description}
Вы ранее записались на это мероприятие""",
        )
