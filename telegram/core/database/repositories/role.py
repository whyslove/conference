from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.expression import select, delete
from typing import Optional, List, Union

from create_table import Role


class RoleRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, value='') -> List[Optional[dict]]:
        """The function of getting all roles from the Role table.

        :param value: person's role name
        :type value: str

        :return: list of dictionaries - json format of the requested object
        :rtype: List[dict | None]

        """

        query = select(Role)

        if value != '':
            query = query.where(Role.value == value)

        roles = [
            {
                'value': role.value
            } for role in (await self.session.execute(query)).scalars()
        ]

        return roles

    async def get_one(self, value='') -> Optional[dict]:
        """The function of getting one role from the Role table.

        :param value: person's role name
        :type value: str

        :return: dictionary - json format of the requested object; or nothing
        :rtype: dict | None

        """

        roles = await self.get_all(
            value=value
        )

        if roles and roles[0]:
            return roles[0]
        return None

    async def delete(self, value='') -> None:
        """The function of deleting roles from the Role table.

        :param value: person's role name
        :type value: str

        :return: nothing
        :rtype: None

        """

        query = delete(Role)

        if value != '':
            query = query.where(Role.value == value)

        await self.session.execute(query)
        await self.session.commit()

        return None

    async def add(self, roles: Union[dict, List[dict]]) -> Union[dict, List[dict]]:
        """The function of adding roles to the Role table.

        :param roles: dictionary or list of dictionaries - json format of the received objects
        :type roles: dict | List[dict]

        :return: dictionary or list of dictionaries - json format of the received objects
        :rtype: dict | List[dict]

        """

        query = select(Role).distinct()
        values = {role.value for role in (await self.session.execute(query)).scalars()}

        if type(roles) == dict:
            roles = [roles]

        return_roles = []

        for role in roles:
            params = {}

            if 'value' in role.keys():
                if role['value'] in values:
                    raise ValueError(f'Unable to add new role with parameter '
                                     f'value="{role["value"]}" '
                                     f'because this value already exists.')
                params['value'] = role['value']
            else:
                raise ValueError(f'Unable to add new role '
                                 f'because a parameter "value" does not exist.')

            self.session.add(Role(**params))
            values.add(params['value'])

            await self.session.commit()
            return_roles.append(params)

        if len(return_roles) == 1:
            return_roles = return_roles[0]

        return return_roles

    async def update(self, value='', new_value='') -> None:
        """The function of updating roles in the Role table.

        :param value: person's role name
        :type value: str

        :param new_value: new person's role name
        :type new_value: str

        :return: nothing
        :rtype: None

        """

        params = dict()
        query = select(Role)

        if value != '':
            params['value'] = value
            query = query.where(Role.value == value)

        if not params:
            return

        roles = (await self.session.execute(query)).scalars()

        query = select(Role).distinct()
        values = {role.value for role in (await self.session.execute(query)).scalars()}

        for role in roles:
            if new_value != '':
                if new_value not in values:
                    values.remove(role.value)
                    role.value = new_value
                    values.add(new_value)
                else:
                    ValueError(f'Unable to update the value in role '
                               f'because role with this '
                               f'value="{new_value}" already exists.')

            await self.session.commit()
