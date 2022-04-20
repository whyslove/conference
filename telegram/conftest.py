import pytest_asyncio
import pytest
import asyncio

from core.database.create_table import SessionLocal
from core.database.repositories import user, token


@pytest_asyncio.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest_asyncio.fixture(scope="session")
async def use_test_guest(event_loop):
    session = SessionLocal()
    ur = user.UserRepository(session=session)

    await ur.add(
        {
            "uid": "testuser1@gmail.com",
            "phone": "+79031281954",
            "snp": "Простой Юзер 1",
            "is_admin": False,
            "tg_chat_id": 123456,
        }
    )
    # await session.close()

    yield

    # session = SessionLocal()
    # ur = user.UserRepository(session=session)
    await ur.delete(uid="testuser1@gmail.com")
    await session.close()


@pytest_asyncio.fixture(scope="session")
async def use_test_admin(event_loop):
    session = SessionLocal()
    ur = user.UserRepository(session=session)
    await ur.add(
        {
            "uid": "testadmin1@gmail.com",
            "phone": "+79031281955",
            "snp": "Простой Админ 1",
            "is_admin": True,
            "tg_chat_id": 654321,
        }
    )

    yield

    await ur.delete(uid="testadmin1@gmail.com")
    session.close()


@pytest_asyncio.fixture(scope="session")
async def use_test_guest2(event_loop):
    session = SessionLocal()
    ur = user.UserRepository(session=session)

    await ur.add(
        {
            "uid": "testuser2@gmail.com",
            "phone": "+79041281958",
            "snp": "Простой Юзер 2",
            "is_admin": False,
            "tg_chat_id": 234567,
        }
    )
    # await session.close()

    yield

    # session = SessionLocal()
    # ur = user.UserRepository(session=session)
    await ur.delete(uid="testuser2@gmail.com")
    await session.close()


@pytest_asyncio.fixture(scope="session")
async def use_test_admin2(event_loop):
    session = SessionLocal()
    ur = user.UserRepository(session=session)
    await ur.add(
        {
            "uid": "testadmin2@gmail.com",
            "phone": "+79041281955",
            "snp": "Простой Админ 2",
            "is_admin": True,
            "tg_chat_id": 765432,
        }
    )

    yield

    await ur.delete(uid="testadmin2@gmail.com")
    session.close()


@pytest_asyncio.fixture(scope="session")
async def use_test_token(event_loop):
    session = SessionLocal()
    tr = token.TokenRepository(session=session)
    await tr.add({"token": "test_token", "vacant": True})

    yield

    await tr.delete(token="test_token")
    session.close()
