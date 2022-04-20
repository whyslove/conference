from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.expression import select, delete
from typing import Optional, List, Union

from ..create_table import Token, User


class TokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, token="", uid="", vacant: Optional[bool] = "") -> List[Optional[dict]]:
        """The function of getting all tokens from the Token table.

        :param token: key to activate a person in the database
        :type token: str

        :param uid: user's unique id
        :type uid: str

        :param vacant: parameter indicating the ability to activate the token
                       (replace None with True)
        :type vacant: bool | None

        :return: list of dictionaries - json format of the requested object
        :rtype: List[dict | None]

        """

        query = select(Token)

        if token != "":
            query = query.where(Token.token == token)

        if vacant != "":
            if vacant is None:
                vacant = True
            query = query.where(Token.vacant == vacant)

        tokens = [
            {"token": token.token, "vacant": token.vacant}
            for token in (await self.session.execute(query)).scalars()
        ]

        return tokens

    async def get_one(self, token="", uid="", vacant: Optional[bool] = "") -> Optional[dict]:
        """The function of getting one token from the Token table.

        :param token: key to activate a person in the database
        :type token: str

        :param uid: user's unique id
        :type uid: str

        :param vacant: parameter indicating the ability to activate the token
                       (replace None with True)
        :type vacant: bool | None

        :return: dictionary - json format of the requested object; or nothing
        :rtype: dict | None

        """

        tokens = await self.get_all(token=token, uid=uid, vacant=vacant)

        if tokens and tokens[0]:
            return tokens[0]
        return None

    async def delete(self, token="", uid="", vacant: Optional[bool] = "") -> None:
        """The function of deleting tokens from the Token table.

        :param token: key to activate a person in the database
        :type token: str

        :param uid: user's unique id
        :type uid: str

        :param vacant: parameter indicating the ability to activate the token
                       (replace None with True)
        :type vacant: bool | None

        :return: nothing
        :rtype: None

        """

        query = delete(Token)

        if token != "":
            query = query.where(Token.token == token)

        if uid != "":
            query = query.where(Token.uid == uid)

        if vacant != "":
            if vacant is None:
                vacant = True
            query = query.where(Token.vacant == vacant)

        await self.session.execute(query)
        await self.session.commit()

        return None

    async def add(self, tokens: Union[dict, List[dict]]) -> Union[dict, List[dict]]:
        """The function of adding tokens to the Token table.

        :param tokens: dictionary or list of dictionaries - json format of the received objects
        :type tokens: dict | List[dict]

        :return: dictionary or list of dictionaries - json format of the received objects
        :rtype: dict | List[dict]

        """

        query = select(Token).distinct()
        token_tokens = {token.token for token in (await self.session.execute(query)).scalars()}
        query = select(User).distinct()
        uids = {user.uid for user in (await self.session.execute(query)).scalars()}

        if type(tokens) == dict:
            tokens = [tokens]

        return_tokens = []

        for token in tokens:
            params = {}

            if "token" in token.keys():
                if token["token"] in token_tokens:
                    raise ValueError(
                        f"Unable to add new token with parameter "
                        f'token="{token["token"]}" '
                        f"because this value already exists."
                    )
                params["token"] = token["token"]
            else:
                raise ValueError(
                    f"Unable to add new token " f'because a parameter "token" does not exist.'
                )

            # if "uid" in token.keys():
            #     if token["uid"] not in uids:
            #         raise ValueError(
            #             f"Unable to add new token "
            #             f"because user with this "
            #             f'uid="{token["uid"]}" does not exist'
            #         )
            #     params["uid"] = token["uid"]
            # else:
            #     raise ValueError(
            #         f"Unable to add new token " f'because a parameter "uid" does not exist.'
            #     )

            if "vacant" in token.keys():
                params["vacant"] = token["vacant"]
            else:
                params["vacant"] = True

            self.session.add(Token(**params))
            token_tokens.add(params["token"])

            await self.session.commit()
            return_tokens.append(params)

        if len(return_tokens) == 1:
            return_tokens = return_tokens[0]

        return return_tokens

    async def update(
        self,
        token="",
        uid="",
        vacant: Optional[bool] = "",
        new_token="",
        new_uid="",
        new_vacant: Optional[bool] = "",
    ) -> None:
        """The function of updating tokens in the Token table.

        :param token: key to activate a person in the database
        :type token: str

        :param uid: user's unique id
        :type uid: str

        :param vacant: parameter indicating the ability to activate the token
                       (replace None with True)
        :type vacant: bool | None

        :param new_token: new key to activate a person in the database
        :type new_token: str

        :param new_uid: new user's unique id
        :type new_uid: str

        :param new_vacant: new parameter indicating the ability to activate the token
                       (replace None with True)
        :type new_vacant: bool | None

        :return: nothing
        :rtype: None

        """

        params = dict()
        query = select(Token)

        if token != "":
            params["token"] = token
            query = query.where(Token.token == token)

        if uid != "":
            params["uid"] = uid
            query = query.where(Token.uid == uid)

        if vacant != "":
            if vacant is None:
                vacant = True
            params["vacant"] = vacant
            query = query.where(Token.vacant == vacant)

        if not params:
            return

        tokens = (await self.session.execute(query)).scalars()

        query = select(Token).distinct()
        token_tokens = {token.token for token in (await self.session.execute(query)).scalars()}
        query = select(User).distinct()
        uids = {user.uid for user in (await self.session.execute(query)).scalars()}

        for token in tokens:
            if new_token != "":
                if new_token not in token_tokens:
                    token_tokens.remove(token.token)
                    token.token = new_token
                    token_tokens.add(new_token)
                else:
                    ValueError(
                        f"Unable to update the value in token "
                        f"because token with this "
                        f'token="{new_token}" already exists.'
                    )

            if new_uid != "":
                if new_uid in uids:
                    token.uid = new_uid
                else:
                    ValueError(
                        f"Unable to update the value in token "
                        f"because user with this "
                        f'uid="{new_uid}" does not exist.'
                    )

            if new_vacant != "":
                token.vacant = new_vacant

            await self.session.commit()
