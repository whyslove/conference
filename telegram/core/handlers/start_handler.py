from cgitb import text
import email
import aiohttp

from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from loguru import logger
from core.config import config
from core.keyboards.all_keyboards import all_keyboards
from core.database.repositories import token, user
from core.database.create_table import SessionLocal
from core.database.repositories import token


async def ask_email(message: types.Message, state: FSMContext):
    await message.answer("Для того, чтобы войти, введите email")
    await state.set_state("need_enter_email")


async def check_email(message: types.Message, state: FSMContext):
    """Asks email and if email exist assign special state according to its role. Then updates db with tg_chat_id"""

    logger.info(f"Receive message from tg {message.text}")
    ur = user.UserRepository(session=SessionLocal())
    # TODO send email on email to condirm identity

    email = message.text.rstrip().lstrip().lower()

    user_ = await ur.get_one(uid=email)

    if not user_:
        logger.info(f"Unknown email {email}")
        await message.answer("Неправильный email, чтобы войти попробуйте ввести его ещё раз")
        await ur.session.close()
        return

    if user_["is_admin"]:
        role = "moderator"
    else:
        role = "guest"

    if await ur.get_one(tg_chat_id=message.from_user.id) != None:
        await ur.update(tg_chat_id=message.from_user.id, new_tg_chat_id=None)
        await ur.update(uid=email, new_tg_chat_id=message.from_user.id)
    else:
        await ur.update(uid=email, new_tg_chat_id=message.from_user.id)

    match role:
        case "moderator":
            logger.debug("Finally it is moderator")
            await state.set_state("moderator_main")
            await message.answer(
                "Ваша почта подтверждена. Для навигации используйте кнопки в меню",
                reply_markup=all_keyboards["moderator_menu"](),
            )
        case "guest":
            logger.debug("Finally it is guest")
            await state.set_state("guest_main")
            await message.answer(
                "Ваша почта подтверждена. Для навигации используйте кнопки в меню",
                reply_markup=all_keyboards["guest_menu"](),
            )

        case _:
            logger.info(f"Unknown role f{email}")
            await message.answer("Неправильный email, чтобы войти попробуйте ввести его ещё раз")

    await ur.session.close()


async def commands(message: types.Message, state: FSMContext):
    match message.text[1:]:  # escape forwarding slash
        case "start":
            await message.answer("Для того, чтобы войти, введите email")
            await state.set_state("need_enter_email")
        case "stop":
            await message.answer("Вы отключились от бота. Зайдите заново с помощью команды /start")
            await state.reset_data()
            await state.reset_state()
        case "menu":
            ur = user.UserRepository(session=SessionLocal())
            _user = await ur.get_one(tg_chat_id=message.from_user.id)
            if not _user:
                await message.answer("Для начала работы введите свою почту")
            elif _user["is_admin"]:
                await message.answer("Показ меню", reply_markup=all_keyboards["moderator_menu"]())
            else:
                await message.answer("Показ меню", reply_markup=all_keyboards["guest_menu"]())
            await ur.session.close()
        case "help":
            await message.answer(
                "Страничка помощи:\n\
            /start начать работу бота и приступить к авторизации через почту\n\
            /stop сбросить состояние бота \n\
            /menu показать меню c кнопками \n\
            /help показать помощь"
            )
