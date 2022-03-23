import json
from datetime import datetime
from pathlib import Path

import openpyxl
from loguru import logger
import httpx

from core.database.repositories import user, speech, user_speech, role
from core.database.create_table import SessionLocal
from core.config import config
from .utils import process_str_data

ROLE_GUEST = "0"
ROLE_SPEAKER = "1"


async def parse_xlsx(full_path: str, admin_tg_id: str) -> str:
    """Replace all database with info from this xlsx file

    Args:
        full_path (str): full path to xlsx file

    Returns:
        str: Error or None
    """
    session = SessionLocal()
    ur = user.UserRepository(session=session)
    rr = role.RoleRepository(session=session)
    sr = speech.SpeechRepository(session=session)
    usr = user_speech.UserSpeechRepository(session=session)

    # temp save of admin
    save_usr = await ur.get_one(tg_chat_id=admin_tg_id)
    # end temp save of admin
    await delete_all_data_in_tables()
    # start temp insert of admin
    await ur.add({
        "uid": save_usr["uid"],
        "snp": save_usr["snp"],
        "phone": save_usr["phone"],
        "tg_chat_id": save_usr["tg_chat_id"],
        "is_admin": save_usr["is_admin"],
    })
    # end temp insert of admin

    xlsx_file = Path(full_path)
    xlsx_obj = openpyxl.load_workbook(xlsx_file)

    await rr.add({"value": ROLE_GUEST})  # dumb guest
    await rr.add({"value": ROLE_SPEAKER})  # chad speaker

    members_data = xlsx_obj["Участники"].values
    _ = next(members_data)  # skip title
    for row in members_data:  # *_ to store blank cells
        email, fio, phone, is_admin, *_ = process_str_data(row)
        if not email:
            break
        if email == save_usr["uid"]:  # temp save admin
            continue  # temp save admin
        try:
            await ur.add({"uid": email, "snp": fio, "phone": phone, "is_admin": is_admin})
        except Exception as exp:
            logger.error(exp)
            return f"Произошла ошибка при обработке листа 'Участники' и человека {fio} с почтой {email}.\n" \
                   f"Внесите изменения и загрузите файл повторно."

    event_data = xlsx_obj["Событие"].values
    _ = next(event_data)  # skip title
    for row in event_data:
        title, speakers, start, end, place, desc_place, *_ = process_str_data(row)  # *_ to store blank cells
        if not title:
            break
        desc_lines = desc_place.split('\n')
        desc_content = [{'tag': 'p', 'children': [line]} for line in desc_lines]
        desc_content = json.dumps(desc_content)
        params = {
            'access_token': config.TELEGRAPH_TOKEN,
            'title': title,
            'author_name': 'Olamia',
            'author_url': 'https://t.me/olamiaconfbot',
            'content': desc_content,
        }
        async with httpx.AsyncClient() as client:  # TODO Telegraph timeout
            response = await client.get('https://api.telegra.ph/createPage', params=params)
        resp_json = response.json()
        if resp_json['ok']:
            desc_link = response.json()['result']['url']
        else:
            desc_link = desc_place
        try:
            res = await sr.add({
                "title": title,
                "start_time": datetime.strptime(start, "%Y-%m-%d %H:%M:%S"),
                "end_time": datetime.strptime(start, "%Y-%m-%d %H:%M:%S"),
                "venue": place,
                "venue_description": desc_link,
            })
            for speaker in speakers.split(";"):
                speaker = process_str_data([speaker])[0]
                await usr.add({"uid": speaker, "key": res["key"], "role": ROLE_SPEAKER})
        except Exception as exp:
            logger.error(exp)
            return f"Произошла ошибка при обработке листа 'События' и строки с названием {title}," \
                   f"временем начала {start}, меcтом {place}.\n" \
                   f"Внесите изменения и загрузите файл повторно."

    session.close()


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
