import asyncio

from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.sql.sqltypes import String, Boolean, BigInteger, DateTime
from sqlalchemy.sql.schema import Column, ForeignKey, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession

from uuid import uuid4 as create_uuid

from .config import settings


convention = {
    "all_column_names": lambda constraint, table: "_".join(
        [column.name for column in constraint.columns.values()]
    ),
    "ix": "ix__%(table_name)s__%(all_column_names)s",
    "uq": "uq__%(table_name)s__%(all_column_names)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": ("fk__%(table_name)s__%(all_column_names)s__" "%(referred_table_name)s"),
    "pk": "pk__%(table_name)s",
}

engine = create_async_engine(
    settings.DB_PATH,
    # connect_args={"check_same_thread": False},  # use this with SQLite
    # echo=True,
)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False, class_=AsyncSession
)

meta = MetaData(naming_convention=convention)
Base = declarative_base(metadata=meta)


class User(Base):
    """Object in the user table in db.

    uid – unique id
    snp – user's surname, name, patronymic
    phone – user's phone number
    is_admin – parameter indicating the presence of admin rights
    tg_chat_id – user's tg chat id

    """

    __tablename__ = "user"

    uid = Column(String, primary_key=True, default=str(create_uuid))
    snp = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    tg_chat_id = Column(BigInteger, unique=True, nullable=True)


class Speech(Base):
    """Object in the speech table in db.

    key – unique code of speech
    title – topic of speech
    start_time – start time of speech
    end_time – end time of speech
    venue – venue for the speaker
    venue_description – description of venue

    """

    __tablename__ = "speech"

    key = Column(String, primary_key=True, default=str(create_uuid))
    title = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    venue = Column(String, nullable=False)
    venue_description = Column(String, nullable=False)


class Role(Base):
    """Object in the role table in db.

    value – person's role name

    """

    __tablename__ = "role"

    value = Column(String, primary_key=True)


class UserSpeech(Base):
    """Object in the user_speech table in db.

    uid – user's unique id
    key – speech's unique id
    role – person's role name
    acknowledgment – confirmation of notification

    """

    __tablename__ = "user_speech"

    uid_key = Column(String, primary_key=True)
    uid = Column(
        String, ForeignKey(User.uid, onupdate="cascade", ondelete="cascade"), nullable=False
    )
    key = Column(
        String, ForeignKey(Speech.key, onupdate="cascade", ondelete="cascade"), nullable=False
    )
    role = Column(
        String, ForeignKey(Role.value, onupdate="cascade", ondelete="cascade"), nullable=False
    )
    acknowledgment = Column(String, default=None, nullable=True)


class Token(Base):
    """Object in the token table in db.

    token – key to activate a person in the database
    uid – user's unique id
    vacant – parameter indicating the ability to activate the token

    """

    __tablename__ = "token"

    token = Column(String, primary_key=True)
    # uid = Column(
    #     String, ForeignKey(User.uid, onupdate="cascade", ondelete="cascade"), nullable=False
    # )
    vacant = Column(Boolean, default=True, nullable=False)


# create tables
async def update_tables(dev=False):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if dev:
        from tests.test_all import TestBase

        testing = TestBase(Base)
        await testing.start()

    print("DB - OK")
    return 0


if __name__ == "__main__":
    # uncomment to test all db functions
    asyncio.run(update_tables(dev=False))
