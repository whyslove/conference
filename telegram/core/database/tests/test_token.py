from tests.test_data import tokens, users

from repositories.token import TokenRepository


async def start(SessionLocal):
    print('----------START INTERACTION WITH TOKENS---------')

    async with SessionLocal() as session:
        repository = TokenRepository(session)

        # adding items does not throw exceptions
        await repository.add(tokens)  # no exceptions

        try:
            await repository.add(tokens)
        except Exception as e:
            assert type(e) == ValueError
        else:
            assert False

        # updating all data for all parameters does not throw exceptions
        old_token = tokens[1]['token']
        await repository.update()  # empty query throws no exceptions
        # updating zero amount of data does not change the item
        assert await repository.get_one(token=tokens[1]['token']) == tokens[1]
        await repository.update(token=tokens[1]['token'])
        assert await repository.get_one(token=tokens[1]['token']) == tokens[1]
        await repository.update(new_token='100000000')
        assert await repository.get_one(token='100000000') is None  # no update is performed without input data

        await repository.update(token=tokens[1]['token'], new_uid=users[50]['uid'])
        assert await repository.get_one(uid=users[50]['uid']) is not None  # updating by token

        await repository.update(token=tokens[1]['token'], uid=users[50]['uid'], new_vacant=not tokens[1]['vacant'])
        assert await repository.get_one(uid=users[50]['uid'], vacant=not tokens[1]['vacant']) is not None  # updating by uid

        await repository.update(token=tokens[1]['token'], uid=users[50]['uid'], vacant=not tokens[1]['vacant'], new_token='new token')
        assert await repository.get_one(token='new token') is not None  # updating by vacant

        assert await repository.get_one(token=old_token) is None  # data changes, not new ones are created
        del old_token

        # does not delete non-existent elements and does not throw exceptions
        old_number = len(await repository.get_all())
        await repository.delete(token='123')  # no exceptions
        assert old_number == len(await repository.get_all())  # the number of elements has not changed
        del old_number

        # deletes by parameter
        assert await repository.add(tokens[1]) == tokens[1]
        assert await repository.get_one(token=tokens[1]['token']) is not None  # element exists
        await repository.delete(token=tokens[1]['token'])  # no exceptions
        assert await repository.get_one(token=tokens[1]['token']) is None  # element deleted

        assert await repository.add(tokens[1]) == tokens[1]
        assert await repository.get_one(uid=tokens[1]['uid']) is not None  # element exists
        await repository.delete(uid=tokens[1]['uid'])  # no exceptions
        assert await repository.get_one(uid=tokens[1]['uid']) is None  # element deleted

        assert await repository.add(tokens[1]) == tokens[1]
        assert await repository.get_one(vacant=tokens[1]['vacant']) is not None  # element exists
        await repository.delete(vacant=tokens[1]['vacant'])  # no exceptions
        assert await repository.get_one(vacant=tokens[1]['vacant']) is None  # element deleted

        # return of modified data
        await repository.delete()
        await repository.add(tokens)

        # close session
        await session.close()

    print('---------FINISH INTERACTION WITH TOKENS--------\n')
