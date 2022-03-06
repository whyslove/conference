"""Module to declare event status handler."""
from aiogram import types
from loguru import logger
from core.keyboards.all_keyboards import all_keyboards
from core.database.create_table import SessionLocal
from core.database.repositories.speech import SpeechRepository
from core.database.repositories.user_speech import UserSpeechRepository
from core.database.repositories.user import UserRepository


async def add_event(callback: types.CallbackQuery):
    """Adds event to personal schedule and make a job for reminder

    :param callback: Callback instance
    :type callback: types.CallbackQuery
    """
    event_id = callback.data.split(":")[1]
    logger.debug(f"Guest {callback.from_user} chose to add {event_id}")
    session = SessionLocal()
    speech_repo = SpeechRepository(session=session)
    target_event = await speech_repo.get_one(key=event_id)
    user_speech_repo = UserSpeechRepository(session)
    user_repo = UserRepository(session)
    user = await user_repo.get_one(tg_chat_id=callback.from_user.id)
    us = await user_speech_repo.get_one(user["uid"], role="0", key=target_event["key"])
    user_speech_list = await user_speech_repo.get_all(user["uid"], role="0")
    # check added before
    added = not us == None
    if added:
        logger.debug(f"Event {event_id} was added before by guest {callback.from_user}")
        await callback.message.delete_reply_markup()
        await callback.message.edit_text(
            callback.message.text + "\nВы выбрали это мероприятие раньше"
        )
    else:
        intersection = False
        for user_speech in user_speech_list:
            event = await speech_repo.get_one(key=user_speech["key"])
            # check intersections
            intersection_event_id = int()
            if (
                event["start_time"] <= target_event["start_time"]
                and target_event["start_time"] <= event["end_time"]
            ):
                intersection = True
                intersection_event_id = event["key"]
        if intersection:
            logger.debug(
                f"Event {event_id} intersects with {intersection_event_id} by guest {callback.from_user}"
            )
            await callback.answer(
                "Невозможно выбрать это мероприятие, так как у вас образовывается пересечение",
                show_alert=True,
            )
        else:
            await user_speech_repo.add(
                {"uid": user["uid"], "key": target_event["key"], "role": "0"}
            )
            logger.debug(f"Event {event_id} was successfully added by guest {callback.from_user}")
            await callback.message.delete_reply_markup()
            await callback.message.edit_text(callback.message.text + "\nВы выбрали это мероприятие")
            # TODO Create a job to make a notification
    await session.close()


async def remove_event_guest(callback: types.CallbackQuery):
    """Removes guest event to personal schedule and delete a job for reminder

    :param callback: Callback instance
    :type callback: types.CallbackQuery
    """
    event_id = callback.data.split(":")[1]
    logger.debug(f"Guest {callback.from_user} chose to remove {event_id}")
    session = SessionLocal()
    user_repo = UserRepository(session)
    user = await user_repo.get_one(tg_chat_id=callback.from_user.id)
    user_speech_repo = UserSpeechRepository(session)
    user_speech_repo.delete(uid=user["uid"], key=event_id, role="0")
    logger.debug(f"Event {event_id} was successfully deleted by guest {callback.from_user}")
    await session.close()
    # delete a job to make a notification
    await callback.message.delete()


async def remove_event_speaker(callback: types.CallbackQuery):
    """Removes speaker event to personal schedule and delete a job for reminder

    :param callback: Callback instance
    :type callback: types.CallbackQuery
    """
    event_id = callback.data.split(":")[1]
    logger.debug(f"Guest {callback.from_user} chose to remove {event_id}")
    session = SessionLocal()
    user_repo = UserRepository(session)
    user = await user_repo.get_one(tg_chat_id=callback.from_user.id)
    user_speech_repo = UserSpeechRepository(session)
    user_speech_repo.delete(uid=user["uid"], key=event_id, role="1")
    logger.debug(f"Event {event_id} was successfully deleted by speaker {callback.from_user}")
    await session.close()
    # delete a job to make a notification
    await callback.message.delete()
