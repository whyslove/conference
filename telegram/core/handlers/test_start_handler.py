from unittest.mock import AsyncMock


import pytest
from core.keyboards.all_keyboards import all_keyboards
from .start_handler import ask_email, check_email, commands


@pytest.mark.asyncio
async def test_ask_email_handler():
    message_answer_correct = "Для того, чтобы войти, введите email"
    state_correct = "need_enter_email"

    message_mock = AsyncMock(text="")
    state_mock = AsyncMock(text="")

    await ask_email(message=message_mock, state=state_mock)

    message_mock.answer.assert_called_with(message_answer_correct)
    state_mock.set_state.assert_called_with(state_correct)


@pytest.mark.asyncio
async def test_check_non_validating_email():
    # мыло, которое не валидируется
    message_answer_correct = "Ваш email не прошёл валидацию. Пожалуйста, попробуйте ещё раз или свяжитесь с администратором"
    message_mock = AsyncMock(text="NOT EMAIL")
    state_mock = AsyncMock(text="")

    await check_email(message=message_mock, state=state_mock)

    message_mock.answer.assert_called_with(message_answer_correct)


@pytest.mark.asyncio
async def test_check_non_existing_email(use_test_guest):
    # мыло, которого пока нет в базе
    message_answer_correct = "Вашего email нет в базе данных. Попробуйте ещё раз"
    message_mock = AsyncMock(text="testuser0@gmail.com")
    state_mock = AsyncMock(text="")

    await check_email(message=message_mock, state=state_mock)

    message_mock.answer.assert_called_with(message_answer_correct)


@pytest.mark.asyncio
async def test_existing_guest_entrance(use_test_guest):
    # перелогиненый гость, который гость
    message_answer_correct = "Ваша почта подтверждена. Для навигации используйте кнопки в меню"
    answer_reply_markup = all_keyboards["guest_menu"]()
    state_correct = "guest_main"

    message_mock = AsyncMock(text="testuser1@gmail.com", from_user=AsyncMock(id=123456))
    state_mock = AsyncMock(text="")

    await check_email(message=message_mock, state=state_mock)

    message_mock.answer.assert_called_with(message_answer_correct, reply_markup=answer_reply_markup)
    state_mock.set_state.assert_called_with(state_correct)


@pytest.mark.asyncio
async def test_existing_admin_entrance(use_test_admin):
    # перелогинение админа
    message_answer_correct = "Ваша почта подтверждена. Для навигации используйте кнопки в меню"
    answer_reply_markup = all_keyboards["moderator_menu"]()
    state_correct = "moderator_main"

    message_mock = AsyncMock(text="testadmin1@gmail.com", from_user=AsyncMock(id=654321))
    state_mock = AsyncMock(text="")

    await check_email(message=message_mock, state=state_mock)

    message_mock.answer.assert_called_with(message_answer_correct, reply_markup=answer_reply_markup)
    state_mock.set_state.assert_called_with(state_correct)


@pytest.mark.asyncio
async def test_login_from_old_device_to_new_profile(use_test_guest):
    #
    message_answer_correct = (
        "Ваш телеграм id не найден. Вы либо зашли впервые, либо зашли с другого аккаунта. "
        "Мы отправили на данную почту сообщение. Пройдите, пожалуйста, по ссылке в нём, чтобы "
        "подтвердить, что эта почта принадлежит вам. После подтверждения бот вам снова напишет"
    )

    message_mock = AsyncMock(text="testuser1@gmail.com", from_user=AsyncMock(id=100000))  # wrong id
    state_mock = AsyncMock(text="")

    await check_email(message=message_mock, state=state_mock)

    message_mock.answer.assert_called_with(message_answer_correct)


@pytest.mark.asyncio
async def test_start_stop_hekp_commands():
    # /start
    message_answer_correct = "Для того, чтобы войти, введите email"
    state_correct = "need_enter_email"
    message_mock = AsyncMock(text="/start")
    state_mock = AsyncMock()
    await commands(message=message_mock, state=state_mock)

    message_mock.answer.assert_called_with(message_answer_correct)
    state_mock.set_state.called_with(state_correct)

    # /stop
    message_answer_correct = "Вы отключились от бота. Зайдите заново с помощью команды /start"
    message_mock = AsyncMock(text="/stop")
    state_mock = AsyncMock()
    await commands(message=message_mock, state=state_mock)

    message_mock.answer.assert_called_with(message_answer_correct)
    state_mock.reset_data.assert_called_with()
    state_mock.reset_state.assert_called_with()

    # /help
    message_answer_correct = "Страничка помощи:\n\
            /start начать работу бота и приступить к авторизации через почту\n\
            /stop сбросить состояние бота \n\
            /menu показать меню c кнопками \n\
            /help показать помощь"

    message_mock = AsyncMock(text="/help")
    state_mock = AsyncMock()
    await commands(message=message_mock, state=state_mock)
    message_mock.answer.assert_called_with(message_answer_correct)


@pytest.mark.asyncio
async def test_menu_command(use_test_guest, use_test_admin):
    # guest_menu
    message_correct = "Показ меню"
    state_correct = "guest_main"
    rp_correct = all_keyboards["guest_menu"]()

    message_mock = AsyncMock(text="/menu", from_user=AsyncMock(id=123456))
    state_mock = AsyncMock()

    await commands(message=message_mock, state=state_mock)

    message_mock.answer.assert_called_with(message_correct, reply_markup=rp_correct)
    state_mock.set_state.assert_called_with(state_correct)

    # admin menu
    message_correct = "Показ меню"
    state_correct = "moderator_main"
    rp_correct = all_keyboards["moderator_menu"]()

    message_mock = AsyncMock(text="/menu", from_user=AsyncMock(id=654321))
    state_mock = AsyncMock()

    await commands(message=message_mock, state=state_mock)

    message_mock.answer.assert_called_with(message_correct, reply_markup=rp_correct)
    state_mock.set_state.assert_called_with(state_correct)

    # no name menu
    message_correct = "Для начала работы введите свою почту"
    state_correct = "need_enter_email"

    message_mock = AsyncMock(text="/menu", from_user=AsyncMock(id=100000))
    state_mock = AsyncMock()

    await commands(message=message_mock, state=state_mock)

    message_mock.answer.assert_called_with(message_correct)
    state_mock.set_state.assert_called_with(state_correct)
