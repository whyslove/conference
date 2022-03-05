from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.expression import select, delete
from typing import Optional, List, Union

from ..create_table import UserSpeech, User, Speech, Role


class UserSpeechRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
        self, uid="", key="", role="", acknowledgment: Optional[str] = ""
    ) -> List[Optional[dict]]:
        """The function of getting all user_speeches from the UserSpeech table.

        :param uid: unique id
        :type uid: str

        :param key: unique code of user_speech
        :type key: str

        :param role: person's role name
        :type role: str

        :param acknowledgment: confirmation of notification
        :type acknowledgment: str | None

        :return: list of dictionaries - json format of the requested object
        :rtype: List[dict | None]

        """

        query = select(UserSpeech)

        if uid != "":
            query = query.where(UserSpeech.uid == uid)

        if key != "":
            query = query.where(UserSpeech.key == key)

        if role != "":
            query = query.where(UserSpeech.role == role)

        if acknowledgment != "":
            query = query.where(UserSpeech.acknowledgment == acknowledgment)

        user_speeches = [
            {
                "uid_key": user_speech.uid_key,
                "uid": user_speech.uid,
                "key": user_speech.key,
                "role": user_speech.role,
                "acknowledgment": user_speech.acknowledgment,
            }
            for user_speech in (await self.session.execute(query)).scalars()
        ]

        return user_speeches

    async def get_one(
        self, uid="", key="", role="", acknowledgment: Optional[str] = ""
    ) -> Optional[dict]:
        """The function of getting one user_speech from the UserSpeech table.

        :param uid: unique id
        :type uid: str

        :param key: unique code of user_speech
        :type key: str

        :param role: person's role name
        :type role: str

        :param acknowledgment: confirmation of notification
        :type acknowledgment: str | None

        :return: dictionary - json format of the requested object; or nothing
        :rtype: dict | None

        """

        user_speeches = await self.get_all(
            uid=uid, key=key, role=role, acknowledgment=acknowledgment
        )

        if user_speeches and user_speeches[0]:
            return user_speeches[0]
        return None

    async def delete(self, uid="", key="", role="", acknowledgment: Optional[str] = "") -> None:
        """The function of deleting user_speeches from the UserSpeech table.

        :param uid: unique id
        :type uid: str

        :param key: unique code of user_speech
        :type key: str

        :param role: person's role name
        :type role: str

        :param acknowledgment: confirmation of notification
        :type acknowledgment: str | None

        :return: nothing
        :rtype: None

        """

        query = delete(UserSpeech)

        if uid != "":
            query = query.where(UserSpeech.uid == uid)

        if key != "":
            query = query.where(UserSpeech.key == key)

        if role != "":
            query = query.where(UserSpeech.role == role)

        if acknowledgment != "":
            query = query.where(UserSpeech.acknowledgment == acknowledgment)

        await self.session.execute(query)
        await self.session.commit()

        return None

    async def add(self, user_speeches: Union[dict, List[dict]]) -> Union[dict, List[dict]]:
        """The function of adding user_speeches to the UserSpeech table.

        :param user_speeches: dictionary or list of dictionaries - json format of the received objects
        :type user_speeches: dict | List[dict]

        :return: dictionary or list of dictionaries - json format of the received objects
        :rtype: dict | List[dict]

        """

        query = select(UserSpeech).distinct()
        uids = {user_speech.uid for user_speech in (await self.session.execute(query)).scalars()}
        keys = {user_speech.key for user_speech in (await self.session.execute(query)).scalars()}
        uids_keys = {
            user_speech.uid_key for user_speech in (await self.session.execute(query)).scalars()
        }

        query = select(User).distinct()
        user_uids = {user.uid for user in (await self.session.execute(query)).scalars()}
        query = select(Speech).distinct()
        speech_keys = {speech.key for speech in (await self.session.execute(query)).scalars()}
        query = select(Role).distinct()
        role_values = {role.value for role in (await self.session.execute(query)).scalars()}

        if type(user_speeches) == dict:
            user_speeches = [user_speeches]

        return_user_speeches = []

        for user_speech in user_speeches:
            params = {}

            if "uid" in user_speech.keys():
                if user_speech["uid"] not in user_uids:
                    raise ValueError(
                        f"Unable to add new user_speech "
                        f"because user with this "
                        f'uid="{user_speech["uid"]}" does not exist'
                    )
            else:
                raise ValueError(
                    f"Unable to add new user_speech " f'because a parameter "uid" does not exist.'
                )

            if "key" in user_speech.keys():
                if user_speech["key"] not in speech_keys:
                    raise ValueError(
                        f"Unable to add new user_speech "
                        f"because speech with this "
                        f'key="{user_speech["key"]}" does not exist'
                    )
            else:
                raise ValueError(
                    f"Unable to add new user_speech " f'because a parameter "key" does not exist.'
                )

            if f'{user_speech["uid"]}_{user_speech["key"]}' in uids_keys:
                raise ValueError(
                    f"Unable to add new user_speech with parameters "
                    f'uid="{user_speech["uid"]}" and '
                    f'key="{user_speech["key"]}" '
                    f"because this uid and key already exist."
                )

            params["uid_key"] = f'{user_speech["uid"]}_{user_speech["key"]}'
            params["uid"] = user_speech["uid"]
            params["key"] = user_speech["key"]
            uids_keys.add(f'{user_speech["uid"]}_{user_speech["key"]}')

            if "role" in user_speech.keys():
                if user_speech["role"] not in role_values:
                    raise ValueError(
                        f"Unable to add new user_speech "
                        f"because role with this "
                        f'value="{user_speech["role"]}" does not exist'
                    )
                params["role"] = user_speech["role"]
            else:
                raise ValueError(
                    f"Unable to add new user_speech " f'because a parameter "role" does not exist.'
                )

            if "acknowledgment" in user_speech.keys():
                params["acknowledgment"] = user_speech["acknowledgment"]
            else:
                params["acknowledgment"] = None

            self.session.add(UserSpeech(**params))
            uids.add(params["uid"])
            keys.add(params["key"])

            await self.session.commit()
            return_user_speeches.append(params)

        if len(return_user_speeches) == 1:
            return_user_speeches = return_user_speeches[0]

        return return_user_speeches

    async def update(
        self,
        uid="",
        key="",
        role="",
        acknowledgment: Optional[str] = "",
        new_uid="",
        new_key="",
        new_role="",
        new_acknowledgment: Optional[str] = "",
    ) -> None:
        """The function of updating user_speeches in the UserSpeech table.

        :param uid: unique id
        :type uid: str

        :param key: unique code of user_speech
        :type key: str

        :param role: person's role name
        :type role: str

        :param acknowledgment: confirmation of notification
        :type acknowledgment: str | None

        :param new_uid: new unique id
        :type new_uid: str

        :param new_key: new unique code of user_speech
        :type new_key: str

        :param new_role: new person's role name
        :type new_role: str

        :param new_acknowledgment: new confirmation of notification
        :type new_acknowledgment: str | None

        :return: nothing
        :rtype: None

        """

        params = dict()
        query = select(UserSpeech)

        if uid != "":
            params["uid"] = uid
            query = query.where(UserSpeech.uid == uid)

        if key != "":
            params["key"] = key
            query = query.where(UserSpeech.key == key)

        if role != "":
            params["role"] = role
            query = query.where(UserSpeech.role == role)

        if acknowledgment != "":
            params["acknowledgment"] = acknowledgment
            query = query.where(UserSpeech.acknowledgment == acknowledgment)

        if not params:
            return

        user_speeches = (await self.session.execute(query)).scalars()

        query = select(UserSpeech).distinct()
        uids = {user_speech.uid for user_speech in (await self.session.execute(query)).scalars()}
        keys = {user_speech.key for user_speech in (await self.session.execute(query)).scalars()}
        uids_keys = {
            user_speech.uid_key for user_speech in (await self.session.execute(query)).scalars()
        }

        query = select(User).distinct()
        user_uids = {user.uid for user in (await self.session.execute(query)).scalars()}
        query = select(Speech).distinct()
        speech_keys = {speech.key for speech in (await self.session.execute(query)).scalars()}
        query = select(Role).distinct()
        role_values = {role.value for role in (await self.session.execute(query)).scalars()}

        for user_speech in user_speeches:
            if new_uid != "" and new_key != "":
                if new_uid not in user_uids:
                    raise ValueError(
                        f"Unable to update the value in user_speech "
                        f"because user with this "
                        f'uid="{new_uid}" does not exist.'
                    )
                if new_key not in speech_keys:
                    raise ValueError(
                        f"Unable to update the value in user_speech "
                        f"because speech with this "
                        f'key="{new_key}" does not exist.'
                    )
                if f"{new_uid}_{new_key}" in uids_keys:
                    raise ValueError(
                        f"Unable to update the values in user_speech "
                        f"because user_speech with this "
                        f'uid="{new_uid}" and '
                        f'key="{new_key}" already exists.'
                    )
                uids_keys.remove(user_speech.uid_key)
                user_speech.uid_key = f"{new_uid}_{new_key}"
                user_speech.uid = new_uid
                user_speech.key = new_key
                uids_keys.add(user_speech.uid_key)

            elif new_uid != "":
                if new_uid in user_uids:
                    if f"{new_uid}_{user_speech.key}" not in uids_keys:
                        uids_keys.remove(user_speech.uid_key)
                        user_speech.uid_key = f"{new_uid}_{user_speech.key}"
                        user_speech.uid = new_uid
                        uids_keys.add(user_speech.uid_key)
                    else:
                        raise ValueError(
                            f"Unable to update the values in user_speech "
                            f"because user_speech with this "
                            f'uid="{new_uid}" and '
                            f'key="{user_speech.key}" already exists.'
                        )
                else:
                    raise ValueError(
                        f"Unable to update the value in user_speech "
                        f"because user with this "
                        f'uid="{new_uid}" does not exist.'
                    )

            elif new_key != "":
                if new_key in speech_keys:
                    if f"{user_speech.uid}_{new_key}" not in uids_keys:
                        uids_keys.remove(user_speech.uid_key)
                        user_speech.uid_key = f"{user_speech.uid}_{new_key}"
                        user_speech.key = new_key
                        uids_keys.add(user_speech.uid_key)
                    else:
                        raise ValueError(
                            f"Unable to update the values in user_speech "
                            f"because user_speech with this "
                            f'uid="{new_uid}" and '
                            f'key="{user_speech.key}" already exists.'
                        )
                else:
                    raise ValueError(
                        f"Unable to update the value in user_speech "
                        f"because speech with this "
                        f'key="{new_key}" does not exist.'
                    )

            if new_role != "":
                if new_role in role_values:
                    user_speech.role = new_role
                else:
                    raise ValueError(
                        f"Unable to update the value in user_speech "
                        f"because role with this "
                        f'value="{new_role}" does not exist.'
                    )

            if new_acknowledgment != "":
                user_speech.acknowledgment = new_acknowledgment

            await self.session.commit()
