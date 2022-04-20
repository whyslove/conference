import asyncio
from time import sleep
from typing import Dict, Any

from aiogram import types
from loguru import logger

from core import config
from core.utils.reminder import GuestReminder, SpeakerReminder
from core.database.create_table import SessionLocal
from core.database.repositories.speech import SpeechRepository
from core.database.repositories.user_speech import UserSpeechRepository
from core.database.repositories.user import UserRepository


def _events_intersect(event_1: Dict[str, Any], event_2) -> bool:
    return (
        event_1["start_time"] <= event_2["start_time"] <= event_1["end_time"]
        or event_2["start_time"] <= event_1["start_time"] <= event_2["end_time"]
    )


async def add_event(callback: types.CallbackQuery):
    """Adds event to personal schedule and make a job for reminder

    :param callback: Callback instance
    :type callback: types.CallbackQuery
    """
    session = SessionLocal()
    speech_repo = SpeechRepository(session=session)
    user_speech_repo = UserSpeechRepository(session)
    user_repo = UserRepository(session)

    event_id = callback.data.split(":")[1]
    logger.debug(f"Guest {callback.from_user} chose to add {event_id}")

    target_event = await speech_repo.get_one(key=event_id)
    user = await user_repo.get_one(tg_chat_id=callback.from_user.id)
    us = await user_speech_repo.get_one(user["uid"], key=target_event["key"])
    user_speech_list = await user_speech_repo.get_all(user["uid"])
    # check added before
    added = us is not None
    if added:
        logger.debug(f"Event {event_id} was added before by guest {callback.from_user}")
        await callback.message.delete_reply_markup()
        await callback.message.edit_text(
            callback.message.text + "\nВы выбрали это мероприятие раньше"
        )
    else:
        intersection_event_id = None
        for user_speech in user_speech_list:
            event = await speech_repo.get_one(key=user_speech["key"])
            # check intersections
            if _events_intersect(event, target_event):
                intersection_event_id = event["key"]
        if intersection_event_id is not None:
            logger.debug(
                f"Event {event_id} intersects with {intersection_event_id} by guest {callback.from_user}"
            )
            await callback.answer(
                "Невозможно выбрать это мероприятие, так как у вас образуется пересечение",
                show_alert=True,
            )
        else:
            await user_speech_repo.add(
                {"uid": user["uid"], "key": target_event["key"], "role": "0"}
            )
            logger.debug(
                f"Creating a job to event {event_id} which was added by guest {callback.from_user}"
            )
            guest_reminder = GuestReminder(chat_id=callback.from_user.id, event=target_event)
            config.sc.add_remind(guest_reminder)
            logger.debug(f"Event {event_id} was successfully added by guest {callback.from_user}")
            await callback.message.delete_reply_markup()
            await callback.message.edit_text(callback.message.text + "\nВы выбрали это мероприятие")
    await session.close()


async def show_event_description(callback: types.CallbackQuery):
    """Sends event description into chat

    :param callback: Callback instance
    :type callback: types.CallbackQuery
    """
    session = SessionLocal()
    speech_repo = SpeechRepository(session=session)

    event_id = callback.data.split(":")[1]
    logger.debug(f"Sending description of event {event_id} to user {callback.from_user}")

    target_event = await speech_repo.get_one(key=event_id)
    await callback.message.answer(target_event['title'] + "\n" + target_event['venue_description'])

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
    await user_speech_repo.delete(uid=user["uid"], key=event_id, role="0")
    logger.debug(f"Event {event_id} was successfully from db deleted by guest {callback.from_user}")
    logger.debug(
        f"Deleting a job to event {event_id} which was added by guest {callback.from_user}"
    )
    speech_repo = SpeechRepository(session=session)
    target_event = await speech_repo.get_one(key=event_id)
    guest_reminder = GuestReminder(chat_id=callback.from_user.id, event=target_event)
    config.sc.remove_remind(guest_reminder)
    logger.debug(
        f"A job to event {event_id} which was added by guest {callback.from_user} was successfully removed"
    )
    await session.close()
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
    await user_speech_repo.delete(uid=user["uid"], key=event_id, role="1")
    logger.debug(
        f"Event {event_id} was successfully deleted by speaker {callback.from_user} from db"
    )
    speech_repo = SpeechRepository(session=session)
    target_event = await speech_repo.get_one(key=event_id)
    speaker_reminder = SpeakerReminder(email=user["uid"], event=target_event)
    config.sc.remove_remind(speaker_reminder)
    logger.debug(f"Speakers job to event {event_id}  {callback.from_user} was successfully removed")
    moderators_list = await user_repo.get_all(is_admin=True)
    for moderator in moderators_list:
        if moderator:
            # send data to moderator
            if moderator["tg_chat_id"]:
                await callback.bot.send_message(
                    moderator["tg_chat_id"],
                    f"Спикер {user['snp']} решил <b>не пойти</b> на мероприятие <b>\"{target_event['title']}\"</b>",
                    parse_mode="HTML",
                )
            else:
                logger.debug(f"No tg_chat_id for moderator {moderator}")
    
    await session.close()
    await callback.message.delete()
