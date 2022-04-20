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
async def test_full_creation_of_new_user():
    # It looks like an integrational test. Because we have four functions, that get info
    # from user and store it in the local storage.
    # so it it is very hard to write unittest to it
    message_correct1 = (
        "Ваша почта не была найдена в базе. Продолжите создание аккаунта. Введите ФИО"
    )
    message_correct2 = "Введите ваш телефон"
    message_correct3 = "Вы получили права модераторa"
    state_correct1 = "enter_snp_for_token"
    state_correct2 = "enter_phone_for_token"
    state_correct3 = "moderator_main"

    kb_correct = all_keyboards["moderator_menu"]()

    email = "testuser3@gmail.com"
    snp = "Test testovich"
    phone = "89057342781"

    message = AsyncMock(text=email)
    state = AsyncMock()

    await enter_email_for_token(message, state)

    message.answer.assert_called_with(message_correct1)
    state.set_state.assert_called_with(state_correct1)

    message = AsyncMock(text=snp)
    state = AsyncMock()
    await enter_snp_for_token(message, state)

    message.answer.assert_called_with(message_correct2)
    state.set_state.assert_called_with(state_correct2)

    message = AsyncMock(text=phone, from_user=AsyncMock(id=345678))
    state = AsyncMock()
    await enter_phone_for_token(message, state)

    message.answer.assert_called_with(message_correct3, reply_markup=kb_correct)
    state.set_state.assert_called_with(state_correct3)
