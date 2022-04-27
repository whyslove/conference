from typing import Tuple
import aiosmtplib
from aiogram import Dispatcher, Bot
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from core.database.repositories import user
from core.database.create_table import SessionLocal
from core.config import config, bot, redis, dp, jinja_env
from loguru import logger
from core.keyboards.all_keyboards import all_keyboards

import secrets
import aioredis

# from telegram.core.routes import verify


class EmailVerificator:
    def __init__(
        self,
        bot: Bot,
        dispatcher: Dispatcher,
        redis: aioredis.Redis,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        verification_endpoint_url: str,
    ) -> None:
        self.tg_bot = bot
        self.dp = dispatcher
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password

        self.token_bytes = 16
        self.redis = redis
        self.verification_endpoint_url = verification_endpoint_url
        self.smtp = aiosmtplib.SMTP(hostname=self.smtp_host, port=self.smtp_port)

    async def send_email(self, recepient_email: str, recepient_fio: str, tg_chat_id: int):
        """Generate token, save token in redis, encode token in clickable url.
        Then send email to person(who enter email to log in bot) with clickable url.

        Args:
            recepient_email (str): person email from bot input
            recepient_fio (str): fio of person with this email
            tg_chat_id (int): tg_chat_id of person tg client
        """

        logger.info(f"start sending email to {recepient_email}")

        token = await self._generate_token()
        logger.debug(f"generated token is {token}")

        email_chat_id = recepient_email + ";;;;;;;" + str(tg_chat_id)
        await self.redis.set(token, email_chat_id, 60 * 60)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Верификация почты в OlamiaConf"
        msg["From"] = "nvr@miem.hse.ru"
        msg["To"] = recepient_email
        # msg["To"] = "svvoylov@edu.hse.ru"

        verify_url = self.verification_endpoint_url + token
        template = jinja_env.get_template("email_template.html").render(
            url=verify_url, recepient_fio=recepient_fio
        )
        part = MIMEText(template, "html")
        msg.attach(part)

        await self.smtp.connect()
        await self.smtp.starttls()
        await self.smtp.login(username=self.smtp_user, password=self.smtp_password)
        await self.smtp.send_message(msg)
        await self.smtp.quit()

    async def _generate_token(self):
        token = secrets.token_urlsafe(self.token_bytes)
        return token

    async def start_final_verification_process(self, token) -> bool:
        """Function that called from route when user click on url with encoded token
        Try to parse token, check token in db, update user in db, update user state
        and send user a message in tg

        Args:
            token (str): decoded token from url

        Returns:
            bool: is verification was ok or not
        """
        email, chat_id = await self.verify_token(token)
        if not email or not chat_id:
            return False
        logger.debug(f"get from redis {email=}, {chat_id=}")
        chat_id = int(chat_id)
        if not email or not chat_id:
            return False

        ur = user.UserRepository(session=SessionLocal())
        try:
            await ur.update(tg_chat_id=chat_id, new_tg_chat_id=None)
            await ur.update(uid=email, new_tg_chat_id=chat_id)
        except Exception as exp:
            logger.info(f"error in db {exp=}")
            await ur.session.close()
            return False

        await self.inform_user_in_tg(chat_id=chat_id, ur=ur)
        await ur.session.close()
        return True

    async def verify_token(self, token: str) -> Tuple[str, str]:
        """Check and delete token in redis"""
        redis_value = await self.redis.get(token)
        try:
            email, chat_id = redis_value.split(";;;;;;;")
        except Exception as exp:
            logger.error(f"exception while unpacking redis object {exp=}")
            return None, None

        await redis.delete(token)
        return email, chat_id

    async def inform_user_in_tg(self, chat_id: int, ur: user.UserRepository):
        """Update user state and send him a message with buttons"""
        usr = await ur.get_one(tg_chat_id=chat_id)

        if usr["is_admin"]:
            await self.dp.storage.set_state(user=chat_id, state="moderator_main")
            await self.tg_bot.send_message(
                chat_id=chat_id,
                text="Ваша почта подтверждена. Для навигации используйте кнопки в меню",
                reply_markup=all_keyboards["moderator_menu"](),
            )
        else:
            await self.dp.storage.set_state(user=chat_id, state="guest_main")
            await self.tg_bot.send_message(
                chat_id=chat_id,
                text="Ваша почта подтверждена. Для навигации используйте кнопки в меню",
                reply_markup=all_keyboards["guest_menu"](),
            )


email_verificator = EmailVerificator(
    bot=bot,
    dispatcher=dp,
    redis=redis,
    smtp_host=config.SMTP_HOST,
    smtp_port=config.SMTP_PORT,
    smtp_user=config.SMTP_USER,
    smtp_password=config.SMTP_PASSWORD,
    verification_endpoint_url=config.VERIFICATION_URL,
)
