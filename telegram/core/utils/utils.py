import shutil
from typing import Sequence, Any

from loguru import logger
from aiogram import types
from aiogram.dispatcher.storage import FSMContext

from core.database.repositories import user
from core.database.create_table import SessionLocal
from core.keyboards.all_keyboards import all_keyboards


class MyValidationError(Exception):
    pass


def clear_directory(directory_path: str):
    """Delete all direcotry

    Args:
        directory_path (str): directory
    """
    try:
        shutil.rmtree(directory_path)
    except OSError as e:
        logger.error("Error: %s - %s." % (e.filename, e.strerror))


async def reset_base_state(message: types.Message, state: FSMContext):
    """In different situations base states may differ: when we do not know user,
    when he is an admin and when he is a guest"""

    ur = user.UserRepository(session=SessionLocal())

    _user = await ur.get_one(tg_chat_id=message.from_user.id)
    if not _user:  # we do not know this user, he need enter email
        await state.set_state("need_enter_email")
    elif _user["is_admin"]:
        await state.set_state("moderator_main")
        await message.answer(
            text="Возврат в главное меню", reply_markup=all_keyboards["moderator_menu"]()
        )
    else:
        await state.set_state("guest_main")
        await message.answer(
            text="Возврат в главное меню", reply_markup=all_keyboards["guest_menu"]()
        )

    await ur.session.close()
