from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from core.database.repositories import token, user
from core.database.create_table import SessionLocal
from core.utils.utils import reset_base_state
from core.keyboards.all_keyboards import all_keyboards
from loguru import logger


async def start_enter_token(message: types.Message, state: FSMContext):
    logger.debug(f"User want to upgrade to admin")
    await state.set_state("enter_token")
    await message.answer("Введите токен")


async def use_token(message: types.Message, state: FSMContext):
    user_token = message.text.rstrip().lstrip().lower()
    logger.debug(f"Get token, start check it")
    logger.debug(f"Token {user_token}")

    tr = token.TokenRepository(session=SessionLocal())

    if await tr.get_one(token=user_token, vacant=True):
        await state.set_state("enter_email_for_token")
        # await tr.update(token=message.text, new_vacant=False)
        await message.answer("Ваш токен верный, теперь введите вашу почту")
    else:
        await message.answer("Неправильный токен. Вы вернетесь в базовое меню")
        await reset_base_state(message, state)
    await tr.session.close()


async def enter_email_for_token(message: types.Message, state: FSMContext):
    email = message.text.rstrip().lstrip().lower()
    logger.debug(f"Get {email=}, try update")

    ur = user.UserRepository(session=SessionLocal())
    if await ur.get_one(uid=email):  # if it is existing user
        await message.answer(
            "Ваша почта найдена в базе данных. Ваш аккаунт получил права модератора"
        )
        await ur.update(uid=message.text, new_is_admin=True, new_tg_chat_id=message.from_user.id)
        await state.set_state("moderator_main")
        await message.answer("Вот ваше меню", reply_markup=all_keyboards["moderator_menu"]())
    else:  # if db is empty or it is false user
        await message.answer(
            "Ваша почта не была найдена в базе. Продолжите создание аккаунта. Введите ФИО"
        )
        await state.set_state("enter_snp_for_token")
        await state.set_data({"email": email})
    # await message.answer("Вы стали модератором")
    # await message.answer("Вот меню", reply_markup=all_keyboards["moderator_menu"]())

    await ur.session.close()


async def enter_snp_for_token(message: types.Message, state: FSMContext):
    snp = message.text.rstrip().lstrip().lower()
    logger.debug(f"Get {snp=}")

    user_not_saved_data = await state.get_data(default=None)
    logger.debug(f"{user_not_saved_data}")

    if not user_not_saved_data:
        await message.answer("Произошла ошибка при добавлении")
        await reset_base_state(message, state)
        logger.error("Error while getting user info from state stroage")
        return

    user_not_saved_data["snp"] = snp

    await state.update_data(data=user_not_saved_data)
    await state.set_state("enter_phone_for_token")
    await message.answer("Введите ваш телефон")


async def enter_phone_for_token(message: types.Message, state: FSMContext):
    phone = message.text.rstrip().lstrip().lower()
    logger.debug(f"Get {phone=}")

    user_not_saved_data = await state.get_data(default=None)
    logger.debug(f"{user_not_saved_data}")

    if not user_not_saved_data:
        await message.answer("Произошла ошибка при добавлении")
        await reset_base_state(message, state)
        logger.error("Error while getting user info from state stroage")
        return

    ur = user.UserRepository(session=SessionLocal())
    try:
        await ur.add(
            {
                "uid": user_not_saved_data["email"],
                "is_admin": True,
                "snp": user_not_saved_data["snp"],
                "phone": phone,
                "tg_chat_id": message.from_user.id,
            }
        )
    except Exception as exp:
        logger.error(exp)
        if await ur.get_one(phone=phone):
            await message.answer(
                "Такой номер телефона уже зарегистрирован. Пройдите весь этап регистрации заново, пожалуйста"
            )
            await reset_base_state(message, state)
            return
        await message.answer(
            "Произошла ошибка при добавлении в базу данных. Пройдите весь этап регистрации заново, пожалуйста"
        )
        await ur.session.close()
        return

    await state.reset_data()
    await state.set_state("moderator_main")
    await ur.session.close()
    await message.answer(
        "Вы получили права модераторa", reply_markup=all_keyboards["moderator_menu"]()
    )
