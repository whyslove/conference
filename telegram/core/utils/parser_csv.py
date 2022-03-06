from turtle import title
import openpyxl
from pathlib import Path
from core.database.repositories import user, speech, user_speech, role
from core.database.create_table import SessionLocal
from datetime import datetime
from loguru import logger

ROLE_GUEST = "0"
ROLE_SPEAKER = "1"


async def parse_xlsx(full_path: str):
    """Replace all database with info from this xlsx file

    Args:
        full_path (str): full path to xlsx file

    Returns:
        str: Error or None
    """

    await delete_all_data_in_tables()

    xlsx_file = Path(full_path)
    xlsx_obj = openpyxl.load_workbook(xlsx_file)

    rr = role.RoleRepository(session=SessionLocal())
    await rr.add({"value": ROLE_GUEST})  # dumb guest
    await rr.add({"value": ROLE_SPEAKER})  # chad speaker
    await rr.session.close()

    members_data = xlsx_obj["Участники"].values
    ur = user.UserRepository(session=SessionLocal())
    _ = next(members_data)  # skip title
    for email, fio, phone, is_admin, *_ in members_data:  # *_ to store blank cells
        if not email:
            break
        try:
            await ur.add({"uid": email, "snp": fio, "phone": phone, "is_admin": is_admin})
        except Exception as exp:
            logger.error(exp)
            return f"Ошибка на {email=} {fio=}"
    await ur.session.close()

    event_data = xlsx_obj["Событие"].values
    sr = speech.SpeechRepository(session=SessionLocal())
    usr = user_speech.UserSpeechRepository(session=SessionLocal())
    _ = next(event_data)  # skip title
    for title, speakers, start, end, place, desc_place, *_ in event_data:  # *_ to store blank cells
        if not title:
            break
        try:
            res = await sr.add(
                {
                    "title": title,
                    "start_time": datetime.strptime(start, "%Y-%m-%d %H:%M:%S"),
                    "end_time": datetime.strptime(start, "%Y-%m-%d %H:%M:%S"),
                    "venue": place,
                    "venue_description": desc_place,
                }
            )
            for speaker in speakers.split(";"):
                await usr.add({"uid": speaker, "key": res["key"], "role": ROLE_SPEAKER})
        except Exception as exp:
            logger.error(exp)
            return f"Ошибка на {title=}"
    await usr.session.close()
    await sr.session.close()


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
