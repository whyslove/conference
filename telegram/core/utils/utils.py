from pathlib import Path
from loguru import logger
import shutil
from aiogram.dispatcher.storage import FSMContext
from aiogram import types
from core.database.repositories import user
from core.database.create_table import SessionLocal


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
    else:
        await state.set_data("guest_main")

    await ur.session.close()


def process_str_data(array: str):
    """Apply lower, rstrip, lstrip to str"""
    result = []
    for el in array:
        if type(el) == str:
            result.append(el.rstrip().lstrip().lower())
        else:
            result.append(el)
    return result
