import httpx
import json
from datetime import datetime
from loguru import logger
from pathlib import Path

import openpyxl
from validate_email import validate_email
from phonenumbers import carrier, parse
from phonenumbers.phonenumberutil import number_type

from core.config import config
from core.database.repositories import user, speech, user_speech, role
from core.database.create_table import SessionLocal
from .utils import MyValidationError

ROLE_GUEST = "0"
ROLE_SPEAKER = "1"


async def parse_xlsx(full_path: str, admin_tg_id: str):
    """Update database with info from this xlsx
    First work with users. Save those who is now in db in set.
    While processing users from xlsx, add id db those who is not in set and update
    others. Only after updating (not adding) an user we remove him from set. So, after processing all
    users from xlsx, we have in set only users that should be removed

    Same logic applies to events

    Args:
        full_path (str): full path to xlsx file

    Returns:
        str: Error or None
    """
    xlsx_file = Path(full_path)
    xlsx_obj = openpyxl.load_workbook(xlsx_file)

    session = SessionLocal()
    ur = user.UserRepository(session=session)
    rr = role.RoleRepository(session=session)
    sr = speech.SpeechRepository(session=session)
    usr = user_speech.UserSpeechRepository(session=session)

    old_db_emails = set()
    if not await rr.get_one(value=ROLE_GUEST):
        await rr.add({"value": ROLE_GUEST})  # default guest
        await rr.add({"value": ROLE_SPEAKER})  # perfect speaker

    all_users = await ur.get_all()
    logger.debug(f"All users in db: {all_users}")
    for cur_user in all_users:
        old_db_emails.add(cur_user["uid"])

    members_data = xlsx_obj["Участники"].values
    _ = next(members_data)  # skip title
    row_number = 2  # use row number for human readable user erorrs. 1st row is title
    for row in members_data:
        try:
            email, fio, phone, is_admin = process_members_row(row)
        except MyValidationError as exp:
            logger.info(f"Ошибка от пользователя {exp}")
            return f"Произошла ошибка при обработке листа 'Участники', в строке {row_number}. {str(exp)}"
        except Exception as exp:
            logger.error(
                f"Неожиданная ошибка от пользователя при заполнения конфига {exp}. Изначальная строчка {row}"
            )
            return f"Произошла ошибка при обработке листа 'Участники', в строке {row_number}. {str(exp)}"
        if not email or not fio or not phone:
            return f"Произошла ошибка при обработке листа 'Участники', в строке {row_number}. Одна из колонок пуста"
        try:
            if email in old_db_emails:
                await ur.update(uid=email, new_snp=fio, new_phone=phone, new_is_admin=is_admin)
                old_db_emails.remove(email)
            else:
                await ur.add({"uid": email, "snp": fio, "phone": phone, "is_admin": is_admin})
        except Exception as exp:
            logger.error(exp)

            return f"Произошла ошибка при обработке листа 'Участники' в строке {row_number}. \
                Проверьте уникальность вводимых данных или свяжитесь с администратором"
        row_number += 1

    for old_email in old_db_emails:
        await ur.delete(uid=old_email)

    old_db_events = set()
    all_events = await sr.get_all()
    logger.debug(f"All events in db: {all_events}")
    for cur_event in all_events:
        old_db_events.add((cur_event["title"], cur_event["start_time"]))

    event_data = xlsx_obj["Событие"].values
    _ = next(event_data)  # skip title
    row_number = 2

    for row in event_data:
        try:
            title, speakers, start, end, place, desc_place = process_events_row(row)
        except MyValidationError as exp:
            logger.info(f"Ошибка от пользователя {exp}")
            return (
                f"Произошла ошибка при обработке листа 'События', в строке {row_number}. {str(exp)}"
            )
        except Exception as exp:
            logger.error(
                f"Неожиданная ошибка от пользователя при заполнения конфига {exp}. Изначальная строчка {row}"
            )
            return (
                f"Произошла ошибка при обработке листа 'События', в строке {row_number}. {str(exp)}"
            )
        if not title or not speakers or not start or not end or not place:
            return f"Произошла ошибка при обработке листа 'События', в строке {row_number}. Одна из колонок пуста"
        desc_place = (
            (desc_place[:8000] + "...") if len(desc_place) > 8000 else desc_place
        )  # truncate long strings
        desc_lines = desc_place.split("\n")
        data = {
            "access_token": config.TELEGRAPH_TOKEN,
            "title": title,
            "author_name": "Olamia",
            "author_url": "https://t.me/olamiaconfbot",
            "content": json.dumps([{"tag": "p", "children": [line]} for line in desc_lines]),
        }
        try:
            async with httpx.AsyncClient() as client:  # TODO Telegraph timeout
                response = await client.post("https://api.telegra.ph/createPage", data=data)
        except httpx.RequestError:
            return f"Не удалось загрузить описание для строки {row_number}. Нет доступа к Telegraph"
        if response.status_code != httpx.codes.OK:
            logger.error(response)
            return f"Не удалось загрузить описание для строки {row_number}. Ответ {response.status_code}"
        resp_json = response.json()
        if resp_json["ok"]:
            desc_link = response.json()["result"]["url"]
        else:
            logger.error(json.dumps(resp_json))
            logger.error(data["content"])
            return f"Не удалось загрузить описание для строки {row_number}"
        try:
            if (title, start) in old_db_events:
                # I use combination of title and start_time to uniquely identify one record
                await sr.update(
                    title=title,
                    start_time=start,
                    new_end_time=end,
                    new_venue=place,
                    new_venue_description=desc_link,
                )
                old_db_events.remove((title, start))

            else:
                await sr.add(
                    {
                        "title": title,
                        "start_time": start,
                        "end_time": end,
                        "venue": place,
                        "venue_description": desc_link,
                    }
                )
            current_key = (await sr.get_one(title=title, start_time=start))["key"]

            # next we have to handle all speakers like users and events before
            old_db_speakers = set()
            all_old_db_speakers = await usr.get_all(key=current_key, role=ROLE_SPEAKER)

            for old_speaker in all_old_db_speakers:
                old_db_speakers.add(old_speaker["uid"])

            for speaker in speakers:  # speaker is speaker email
                check_existance = await ur.get_one(uid=speaker)
                if not check_existance:
                    logger.debug(f"Error while checking existence of {speaker}")
                    return f"Произошла ошибка при обработке листа 'События', строка {row_number}. \
                        Email одного из спикеров не существует в листе 'Участники'"
                if speaker in old_db_speakers:
                    old_db_speakers.remove(speaker)
                else:
                    await usr.add({"uid": speaker, "key": current_key, "role": ROLE_SPEAKER})

            for old_speaker in old_db_speakers:
                await usr.delete(uid=old_speaker, key=current_key, role=ROLE_SPEAKER)
            row_number += 1

        except Exception as exp:
            logger.error(exp)
            return f"Произошла ошибка при обработке листа 'События', строкa {row_number}. \
                Проверьте корректность вводимых данных."
    for old_event in old_db_events:
        await sr.delete(title=old_event[0], start_time=old_event[1])

    await session.close()


async def delete_all_data_in_tables():
    session = SessionLocal()

    ur = user.UserRepository(session=session)
    sr = speech.SpeechRepository(session=session)
    usr = user_speech.UserSpeechRepository(session=session)
    rr = role.RoleRepository(session=session)

    users = await ur.get_all()
    for _user in users:
        await ur.delete(**_user)

    speeches = await sr.get_all()
    for _spech in speeches:
        await sr.delete(**_spech)

    many_user_spech = await usr.get_all()
    for _user_spech in many_user_spech:
        await usr.delete(**_user_spech)

    await rr.delete(value=ROLE_GUEST)
    await rr.delete(value=ROLE_SPEAKER)

    await session.close()


def process_members_row(row):
    """Process one row in members sheet. Be careful if data schema in xlsx will change
    need to change this function too

    Args:
        row (list): row in format [email, fio, phone, is_admin, *]
    Returns:
        email, fio, phone, is_admin
    """
    email, fio, phone, is_admin, *_ = row  # *_ to store blank cells
    if not email or not fio or not phone or is_admin is None:
        raise MyValidationError("Одна из колонок пуста")
    email = email.rstrip().lstrip().lower()
    fio = fio.rstrip().lstrip()
    phone = phone.rstrip().lstrip()

    if not validate_email(email_address=email, check_smtp=False, check_dns=False):
        raise MyValidationError("Неправильно записан email адрес")
    if not carrier._is_mobile(number_type(parse(phone))):
        raise MyValidationError("Неправильно записан номер телефона")

    return email, fio, phone, is_admin


def process_events_row(row):
    """Process one row in members sheet. Be careful if data schema in xlsx will change
    need to change this function too

    Args:
        row (list): row in format [title, speakers, start, end, place, desc_place, *]
    Returns:
        title: str, speakers: list, start: datetime, end: datetime, place: str, desc_place: str
    """
    title, speakers, start, end, place, desc_place, *_ = row  # *_ to store blank rows
    if not title or not speakers or not start or not end or not place or not desc_place:
        raise MyValidationError("Одна из колонок пуста")
    title = title.rstrip().lstrip()
    speakers = [
        speaker.rstrip().lstrip().lower() for speaker in speakers.split(";")
    ]  # no need here email validation because next we check existance in user_table of this emails
    try:
        start = datetime.strptime(start.rstrip().lstrip(), "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(end.rstrip().lstrip(), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise MyValidationError("Неправильно сформирована дата")
    if end < start:
        raise MyValidationError("Дата конца меньше даты начала")
    place = place.rstrip().lstrip()
    desc_place = desc_place.rstrip().lstrip()
    return title, speakers, start, end, place, desc_place
