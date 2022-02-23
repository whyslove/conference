from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

all_keyboards = {}

# I've used functions because lately info in buttons and their number may differ beacuse
# of different number of days in Conference, so they will have to be dinamically configured
def kb_guest_menu():
    kb_guest = ReplyKeyboardMarkup()
    kb_guest.add(
        KeyboardButton("Общее расписание"),
        KeyboardButton("Моё раписание"),
    )
    return kb_guest


def kb_guest_personal_schedule():
    kb_guest = ReplyKeyboardMarkup()
    kb_guest.add(
        KeyboardButton("Моё расписание на сегодня"),
        KeyboardButton("Моё раписание на завтра"),
        KeyboardButton("Мои неофициальные активности"),
        KeyboardButton("Мои выступления"),
        KeyboardButton("Вернуться в главное меню")
        # TODO dynamically configurred days
    )
    return kb_guest


def kb_moderator_menu():
    kb_moderator = ReplyKeyboardMarkup()
    kb_moderator.add(
        KeyboardButton("Общее расписание"),
        KeyboardButton("Ответы участников"),
    )


def kb_moderator_answers():
    kb_guest = ReplyKeyboardMarkup()
    kb_guest.add(
        KeyboardButton("Вернуться в главное меню")
        # TODO dynamically configurred days
    )
    return kb_guest


all_keyboards["guest_menu"] = kb_guest_menu
all_keyboards["guest_personal_schedule"] = kb_guest_personal_schedule
all_keyboards["moderator_menu"] = kb_moderator_menu
all_keyboards["moderator_answers"] = kb_moderator_answers
