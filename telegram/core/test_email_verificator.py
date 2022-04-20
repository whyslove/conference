from unittest.mock import AsyncMock
from .email_verificator import EmailVerificator
from core.keyboards.all_keyboards import all_keyboards
from core.database.create_table import SessionLocal
from core.database.repositories import user
import pytest


@pytest.mark.asyncio
async def test_final_verification_process(use_test_guest2, use_test_admin2):
    # kind of integrational test
    # we are "relogin" from admin to guest
    # so we check the initial state (with asserting)
    # then check whether user receive keyboard with new state after verification process
    # second check naturally does it all changed
    bot = AsyncMock()
    dispatcher = AsyncMock()
    redis = AsyncMock()
    guest_email = "testuser2@gmail.com"
    admin_email = "testadmin2@gmail.com"
    old_guest_chat_id = 234567
    new_guest_chat_id = 765432
    reply_text_correct = "Ваша почта подтверждена. Для навигации используйте кнопки в меню"
    reply_markup = all_keyboards["guest_menu"]()
    state_correct = "guest_main"

    ur = user.UserRepository(session=SessionLocal())
    user1 = await ur.get_one(tg_chat_id=old_guest_chat_id)
    assert user1["uid"] == guest_email
    user2 = await ur.get_one(tg_chat_id=new_guest_chat_id)
    assert user2["uid"] == admin_email

    email_verificator = EmailVerificator(
        bot=bot,
        dispatcher=dispatcher,
        redis=redis,
        smtp_host="",
        smtp_port="",
        smtp_user="",
        smtp_password="",
        verification_endpoint_url="",
    )

    async def verify_token(_):
        return (guest_email, str(new_guest_chat_id))

    email_verificator.verify_token = verify_token

    await email_verificator.start_final_verification_process("")

    email_verificator.tg_bot.send_message.assert_called_with(
        chat_id=new_guest_chat_id,
        text=reply_text_correct,
        reply_markup=reply_markup,
    )
    dispatcher.storage.set_state.assert_called_with(user=new_guest_chat_id, state=state_correct)

    user1 = await ur.get_one(uid=admin_email)
    assert user1["tg_chat_id"] is None

    user2 = await ur.get_one(tg_chat_id=new_guest_chat_id)
    assert user2["uid"] == guest_email
    await ur.session.close()
