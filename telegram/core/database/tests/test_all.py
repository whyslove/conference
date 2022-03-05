from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.session import sessionmaker

from tests import (
    test_creating,
    test_user,
    test_speech,
    test_role,
    test_user_speech,
    test_token,
    test_dropping
)

from config import settings


class TestBase:
    def __init__(self, base: DeclarativeMeta):
        self.base = base
        self.engine = create_async_engine(settings.DB_PATH)

        self.session_local = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

    async def start(self):
        print('------------------START TESTING------------------\n')

        await test_creating.start(self.session_local)
        await test_dropping.start(self.engine, self.base)
        await test_creating.start(self.session_local)

        await test_user.start(self.session_local)
        await test_speech.start(self.session_local)
        await test_role.start(self.session_local)
        await test_user_speech.start(self.session_local)
        await test_token.start(self.session_local)

        # await test_dropping.start(self.engine, self.base)

        print('------------------FINISH TESTING-----------------')
