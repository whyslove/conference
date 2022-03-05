from tests.test_data import roles

from repositories.role import RoleRepository


async def start(SessionLocal):
    print('----------START INTERACTION WITH ROLES---------')

    async with SessionLocal() as session:
        repository = RoleRepository(session)

        # adding items does not throw exceptions
        await repository.add(roles)  # no exceptions

        try:
            await repository.add(roles)
        except Exception as e:
            assert type(e) == ValueError
        else:
            assert False

        # updating all data for all parameters does not throw exceptions
        old_value = roles[1]['value']
        await repository.update()  # empty query throws no exceptions
        # updating zero amount of data does not change the item
        assert await repository.get_one(value=roles[1]['value']) == roles[1]
        await repository.update(value=roles[1]['value'])
        assert await repository.get_one(value=roles[1]['value']) == roles[1]
        await repository.update(new_value='100000000')
        assert await repository.get_one(value='100000000') is None  # no update is performed without input data

        await repository.update(value=roles[1]['value'], new_value='1 2 3')
        assert await repository.get_one(value='1 2 3') is not None  # updating by uid

        assert await repository.get_one(value=old_value) is None  # data changes, not new ones are created
        del old_value

        # does not delete non-existent elements and does not throw exceptions
        old_number = len(await repository.get_all())
        await repository.delete(value='123')  # no exceptions
        assert old_number == len(await repository.get_all())  # the number of elements has not changed
        del old_number

        # deletes by parameter
        assert await repository.add(roles[1]) == roles[1]
        assert await repository.get_one(value=roles[1]['value']) is not None  # element exists
        await repository.delete(value=roles[1]['value'])  # no exceptions
        assert await repository.get_one(value=roles[1]['value']) is None  # element deleted

        # return of modified data
        await repository.delete()
        await repository.add(roles)

        # close session
        await session.close()

    print('---------FINISH INTERACTION WITH ROLES--------\n')
