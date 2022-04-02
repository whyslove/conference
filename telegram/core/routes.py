from fastapi import APIRouter
from fastapi.responses import HTMLResponse

# from aiogram import types, Dispatcher, Bot
from core.email_verificator import email_verificator
from core.config import jinja_env


router = APIRouter()


@router.get("/verify/{token}")
async def verify(token: str):
    result = await email_verificator.start_final_verification_process(token)

    if not result:
        message = "Ваш токен либо не существует, либо у него истек срок действия"
    else:
        message = "Мы успешно подтвердили ваш аккаунт"
    template = jinja_env.get_template("verify_answer.html").render(message=message)
    return HTMLResponse(content=template)
