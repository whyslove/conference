import pytest
from unittest.mock import AsyncMock
from .token_handlers import (
    start_enter_token,
    use_token,
    enter_email_for_token,
    enter_snp_for_token,
    enter_phone_for_token,
)
from core.keyboards.all_keyboards import all_keyboards
from core.database.repositories import user
from core.database.create_table import SessionLocal


@pytest.mark.asyncio
async def test_start_enter_token():
    message_correct = "Введите токен"
    state_correct = "enter_token"

    message = AsyncMock()
    state = AsyncMock()

    await start_enter_token(message=message, state=state)

    state.set_state.assert_called_with(state_correct)
    message.answer.assert_called_with(message_correct)


@pytest.mark.asyncio
async def test_use_correct_token(use_test_token):
    message_correct = "Ваш токен верный, теперь введите вашу почту"
    state_correct = "enter_email_for_token"
    correct_token = "test_token"

    message = AsyncMock(text=correct_token)
    state = AsyncMock()

    await use_token(message, state)

    message.answer.assert_called_with(message_correct)
    state.set_state.assert_called_with(state_correct)


@pytest.mark.asyncio
async def test_use_incorrect_token(use_test_guest, use_test_token):
    # specially acces on behalf simple user
    # so we have to be returned to the main menu
    message_correct = "Возврат в главное меню"
    state_correct = "guest_main"
    kb_correct = all_keyboards["guest_menu"]()
    incorrect_token = "BAD_test_token"
    test_user_id = 123456

    message = AsyncMock(text=incorrect_token, from_user=AsyncMock(id=test_user_id))
    state = AsyncMock()

    await use_token(message, state)

    message.answer.assert_called_with(text=message_correct, reply_markup=kb_correct)
    state.set_state.assert_called_with(state_correct)


@pytest.mark.asyncio
async def test_bad_email_for_token(use_test_guest):
    # specially acces on behalf simple user
    # so we have to be returned to the main menu
    message_correct = "Некорректный email. Введите его ещё раз"
    existing_email = "Bad@email@testuser1@gmail.com"

    message = AsyncMock(text=existing_email)
    state = AsyncMock()

    await enter_email_for_token(message, state)

    message.answer.assert_called_with(message_correct)


@pytest.mark.asyncio
async def test_enter_existing_email_for_token(use_test_guest):
    # specially acces on behalf simple user
    # so we have to be returned to the main menu
    message_correct = "Вот ваше меню"
    state_correct = "moderator_main"
    existing_email = "testuser1@gmail.com"
    kb_correct = all_keyboards["moderator_menu"]()

    message = AsyncMock(text=existing_email)
    state = AsyncMock()

    await enter_email_for_token(message, state)

    message.answer.assert_called_with(message_correct, reply_markup=kb_correct)
    state.set_state.assert_called_with(state_correct)


@pytest.mark.asyncio
async def test_enter_new_emain_for_token():
    email = "newnewemail@gmail.com"
    message_correct = "Ваша почта не была найдена в базе. Продолжите создание аккаунта. Введите ФИО"
    state_correct = "enter_snp_for_token"
    data_correct = {"email": email}

    message = AsyncMock(text=email)
    state = AsyncMock()
    await enter_email_for_token(message, state)

    message.answer.assert_called_with(message_correct)
    state.set_state.assert_called_with(state_correct)
    state.set_data.assert_called_with(data_correct)


@pytest.mark.asyncio
async def test_enter_snp_for_token():
    # email from prev test
    email = "newnewemail@gmail.com"
    snp = "mysnp"
    message_correct = "Введите ваш телефон"
    state_correct = "enter_phone_for_token"
    message = AsyncMock(text=snp)
    state = AsyncMock()

    async def get_data(default):
        return {"email": email}

    state.get_data = get_data
    await enter_snp_for_token(message, state)

    message.answer.assert_called_with(message_correct)
    state.set_state.assert_called_with(state_correct)
    state.update_data.assert_called_with(data={"email": email, "snp": snp})


@pytest.mark.asyncio
async def test_enter_phone_for_token():
    # email and snp from prev test
    email = "newnewemail@gmail.com"
    snp = "mysnp"
    phone = "+79057342891"
    tg_chat_id = 456789
    message_correct = "Вы получили права модераторa"
    state_correct = "moderator_main"
    kb_correct = all_keyboards["moderator_menu"]()

    message = AsyncMock(text=phone, from_user=AsyncMock(id=tg_chat_id))
    state = AsyncMock()

    async def get_data(default):
        return {"email": email, "snp": snp}

    state.get_data = get_data

    await enter_phone_for_token(message, state)
    message.answer.assert_called_with(message_correct, reply_markup=kb_correct)
    state.set_state_assert_called_with(state_correct)

    ur = user.UserRepository(session=SessionLocal())
    assert (
        await ur.get_one(uid=email, snp=snp, phone=phone, tg_chat_id=tg_chat_id, is_admin=True)
        is not None
    )
    ur.session.close()
