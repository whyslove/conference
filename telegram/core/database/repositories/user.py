from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.expression import select, delete
from typing import Optional, List, Union
from uuid import uuid4 as create_uuid

from ..create_table import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
        self,
        uid: Optional[str] = "",
        snp="",
        phone="",
        is_admin: Optional[bool] = "",
        tg_chat_id: Optional[int] = "",
    ) -> List[Optional[dict]]:
        """The function of getting all users from the User table.

        :param uid: unique id (replace None with new uuid)
        :type uid: str | None

        :param snp: user's surname, name, patronymic
        :type snp: str

        :param phone: user's phone number
        :type phone: str

        :param is_admin: parameter indicating the presence of admin rights (replace None with False)
        :type is_admin: bool | None

        :param tg_chat_id: user's tg chat id
        :type tg_chat_id: int | None

        :return: list of dictionaries - json format of the requested object
        :rtype: List[dict | None]

        """

        query = select(User)

        if uid != "" and uid is not None:
            query = query.where(User.uid == uid)

        if snp != "":
            query = query.where(User.snp == snp)

        if phone != "":
            query = query.where(User.phone == phone)

        if is_admin != "" and is_admin is not None:
            query = query.where(User.is_admin == is_admin)

        if tg_chat_id != "":
            query = query.where(User.tg_chat_id == tg_chat_id)

        users = [
            {
                "uid": user.uid,
                "snp": user.snp,
                "phone": user.phone,
                "is_admin": user.is_admin,
                "tg_chat_id": user.tg_chat_id,
            }
            for user in (await self.session.execute(query)).scalars()
        ]

        return users

    async def get_one(
        self,
        uid: Optional[str] = "",
        snp="",
        phone="",
        is_admin: Optional[bool] = "",
        tg_chat_id: Optional[int] = "",
    ) -> Optional[dict]:
        """The function of getting one user from the User table.

        :param uid: unique id (replace None with new uuid)
        :type uid: str | None

        :param snp: user's surname, name, patronymic
        :type snp: str

        :param phone: user's phone number
        :type phone: str

        :param is_admin: parameter indicating the presence of admin rights (replace None with False)
        :type is_admin: bool | None

        :param tg_chat_id: user's tg chat id
        :type tg_chat_id: int | None

        :return: dictionary - json format of the requested object; or nothing
        :rtype: dict | None

        """

        users = await self.get_all(
            uid=uid, snp=snp, phone=phone, is_admin=is_admin, tg_chat_id=tg_chat_id
        )

        if users and users[0]:
            return users[0]
        return None

    async def delete(
        self,
        uid="",
        snp="",
        phone="",
        is_admin: Optional[bool] = "",
        tg_chat_id: Optional[int] = "",
    ) -> None:
        """The function of deleting users from the User table.

        :param uid: unique id
        :type uid: str

        :param snp: user's surname, name, patronymic
        :type snp: str

        :param phone: user's phone number
        :type phone: str

        :param is_admin: parameter indicating the presence of admin rights (replace None with False)
        :type is_admin: bool | None

        :param tg_chat_id: user's tg chat id
        :type tg_chat_id: int | None

        :return: nothing
        :rtype: None

        """

        query = delete(User)

        if uid != "":
            query = query.where(User.uid == uid)

        if snp != "":
            query = query.where(User.snp == snp)

        if phone != "":
            query = query.where(User.phone == phone)

        if is_admin != "":
            if is_admin is None:
                is_admin = False
            query = query.where(User.is_admin == is_admin)

        if tg_chat_id != "":
            query = query.where(User.tg_chat_id == tg_chat_id)

        await self.session.execute(query)
        await self.session.commit()

        return None

    async def add(self, users: Union[dict, List[dict]]) -> Union[dict, List[dict]]:
        """The function of adding users to the User table.

        :param users: dictionary or list of dictionaries - json format of the received objects
        :type users: dict | List[dict]

        :return: dictionary or list of dictionaries - json format of the received objects
        :rtype: dict | List[dict]

        """

        query = select(User).distinct()
        uids = {user.uid for user in (await self.session.execute(query)).scalars()}
        phones = {user.phone for user in (await self.session.execute(query)).scalars()}
        tg_chat_ids = {user.tg_chat_id for user in (await self.session.execute(query)).scalars()}

        if type(users) == dict:
            users = [users]

        return_users = []

        for user in users:
            params = {}

            if "uid" in user.keys() and user["uid"] is not None:
                if user["uid"] in uids:
                    raise ValueError(
                        f"Unable to add new user with parameter "
                        f'uid="{user["uid"]}" '
                        f"because this uid already exists."
                    )
                params["uid"] = user["uid"]
            else:
                params["uid"] = str(create_uuid())

            if "snp" in user.keys():
                params["snp"] = user["snp"]
            else:
                raise ValueError(
                    f"Unable to add new user " f'because a parameter "snp" does not exist.'
                )

            if "phone" in user.keys():
                if user["phone"] not in phones:
                    params["phone"] = user["phone"]
                    phones.add(user["phone"])
                else:
                    raise ValueError(
                        f"Unable to add new user with parameter "
                        f'phone="{user["phone"]}" '
                        f"because this phone already exists."
                    )
            else:
                raise ValueError(
                    f"Unable to add new user " f'because a parameter "phone" does not exist.'
                )

            if "is_admin" in user.keys():
                params["is_admin"] = user["is_admin"]
            else:
                params["is_admin"] = False

            if "tg_chat_id" in user.keys():
                if user["tg_chat_id"] not in tg_chat_ids or user["tg_chat_id"] is None:
                    params["tg_chat_id"] = user["tg_chat_id"]
                    tg_chat_ids.add(user["tg_chat_id"])
                else:
                    raise ValueError(
                        f"Unable to add new user with parameter "
                        f'tg_chat_id="{user["tg_chat_id"]}" '
                        f"because this tg_chat_id already exists."
                    )
            else:
                params["tg_chat_id"] = None

            self.session.add(User(**params))
            uids.add(params["uid"])

            await self.session.commit()
            return_users.append(params)

        if len(return_users) == 1:
            return_users = return_users[0]

        return return_users

    async def update(
        self,
        uid="",
        snp="",
        phone="",
        is_admin: Optional[bool] = "",
        tg_chat_id: Optional[int] = "",
        new_uid="",
        new_snp="",
        new_phone="",
        new_is_admin: Optional[bool] = "",
        new_tg_chat_id: Optional[int] = "",
    ) -> None:
        """The function of updating users in the User table.

        :param uid: unique id
        :type uid: str

        :param snp: user's surname, name, patronymic
        :type snp: str

        :param phone: user's phone number
        :type phone: str

        :param is_admin: parameter indicating the presence of admin rights (replace None with False)
        :type is_admin: bool | None

        :param tg_chat_id: user's tg chat id
        :type tg_chat_id: int | None

        :param new_uid: new unique id
        :type new_uid: str

        :param new_snp: user's new surname, name, patronymic
        :type new_snp: str

        :param new_phone: user's new phone number
        :type new_phone: str

        :param new_is_admin: new parameter indicating the presence of admin rights
                             (replace None with False)
        :type new_is_admin: bool | None

        :param new_tg_chat_id: user's new tg chat id
        :type new_tg_chat_id: int | None

        :return: nothing
        :rtype: None

        """

        params = dict()
        query = select(User)

        if uid != "":
            params["uid"] = uid
            query = query.where(User.uid == uid)

        if snp != "":
            params["snp"] = snp
            query = query.where(User.snp == snp)

        if phone != "":
            params["phone"] = phone
            query = query.where(User.phone == phone)

        if is_admin != "":
            if is_admin is None:
                is_admin = False
            params["is_admin"] = is_admin
            query = query.where(User.is_admin == is_admin)

        if tg_chat_id != "":
            params["tg_chat_id"] = tg_chat_id
            query = query.where(User.tg_chat_id == tg_chat_id)

        if not params:
            return

        users = (await self.session.execute(query)).scalars()

        query = select(User).distinct()
        uids = {user.uid for user in (await self.session.execute(query)).scalars()}
        phones = {user.phone for user in (await self.session.execute(query)).scalars()}
        tg_chat_ids = {user.tg_chat_id for user in (await self.session.execute(query)).scalars()}

        for user in users:
            if new_uid != "":
                if new_uid not in uids:
                    uids.remove(user.uid)
                    user.uid = new_uid
                    uids.add(new_uid)
                else:
                    ValueError(
                        f"Unable to update the value in user "
                        f"because user with this "
                        f'uid="{new_uid}" already exists.'
                    )

            if new_snp != "":
                user.snp = new_snp

            if new_phone != "":
                if new_phone not in phones:
                    phones.remove(user.phone)
                    user.phone = new_phone
                    phones.add(new_phone)
                else:
                    ValueError(
                        f"Unable to update the value in user "
                        f"because user with this "
                        f'phone="{new_phone}" already exists.'
                    )

            if new_is_admin != "":
                user.is_admin = new_is_admin

            if new_tg_chat_id != "":
                if new_tg_chat_id not in tg_chat_ids:
                    tg_chat_ids.remove(user.tg_chat_id)
                    user.tg_chat_id = new_tg_chat_id
                    tg_chat_ids.add(new_tg_chat_id)
                else:
                    ValueError(
                        f"Unable to update the value in user "
                        f"because user with this "
                        f'tg_chat_id="{new_tg_chat_id}" already exists.'
                    )

            await self.session.commit()
