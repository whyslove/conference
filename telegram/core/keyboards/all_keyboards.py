from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

all_keyboards = {}

# I've used functions because lately info in buttons and their number may differ beacuse
# of different number of days in Conference, so they will have to be dinamically configured
def kb_guest_menu():
    kb_guest = ReplyKeyboardMarkup()
    kb_guest.add(
        KeyboardButton("Общее расписание"),
        KeyboardButton("Моё раcписание"),
    )
    return kb_guest


def kb_guest_personal_schedule():
    kb_guest = ReplyKeyboardMarkup()
    kb_guest.add(
        KeyboardButton("Сегодня"),
        KeyboardButton("Завтра"),
        KeyboardButton("Весь период"),
        KeyboardButton("Выступления"),
        KeyboardButton("Вернуться в главное меню")
        # TODO dynamically configurred days
    )
    return kb_guest


def kb_moderator_menu():
    kb_moderator = ReplyKeyboardMarkup()
    kb_moderator.add(
        KeyboardButton("Общее расписание"),
        KeyboardButton("Ответы участников"),
        KeyboardButton("Загрузить расписание"),
    )
    return kb_moderator


def kb_go_back_button():
    kb_back = ReplyKeyboardMarkup()
    kb_back.add(KeyboardButton("Вернуться назад"))
    return kb_back


def kb_moderator_answers():
    kb_guest = ReplyKeyboardMarkup()
    kb_guest.add(
        KeyboardButton("Вернуться в главное меню")
        # TODO dynamically configurred days
    )
    return kb_guest


def kb_add_event(id: str):
    kb_event = InlineKeyboardMarkup()
    kb_event.add(InlineKeyboardButton(text="Добавить", callback_data="add:" + id))
    return kb_event


def kb_remove_event(id: str):
    kb_event = InlineKeyboardMarkup()
    kb_event.add(InlineKeyboardButton(text="Убрать", callback_data="removeGuest:" + id))
    return kb_event


def kb_remove_speaker(id: str):
    kb_speech = InlineKeyboardMarkup()
    kb_speech.add(InlineKeyboardButton(text="Отказаться", callback_data="removeSpeaker:" + id))
    return kb_speech


all_keyboards["guest_menu"] = kb_guest_menu
all_keyboards["guest_personal_schedule"] = kb_guest_personal_schedule
all_keyboards["moderator_menu"] = kb_moderator_menu
all_keyboards["moderator_answers"] = kb_moderator_answers
all_keyboards["add_event"] = kb_add_event
all_keyboards["remove_event"] = kb_remove_event
all_keyboards["remove_speaker"] = kb_remove_speaker
all_keyboards["back_button"] = kb_go_back_button
