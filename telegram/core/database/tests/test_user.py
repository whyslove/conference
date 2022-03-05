from tests.test_data import users

from repositories.user import UserRepository


async def start(SessionLocal):
    print('----------START INTERACTION WITH USERS---------')

    async with SessionLocal() as session:
        repository = UserRepository(session)

        # adding items does not throw exceptions
        await repository.add(users)  # no exceptions

        try:
            await repository.add(users)
        except Exception as e:
            assert type(e) == ValueError
        else:
            assert False

        # updating all data for all parameters does not throw exceptions
        old_uid = users[1]['uid']
        await repository.update()  # empty query throws no exceptions
        # updating zero amount of data does not change the item
        assert await repository.get_one(uid=users[1]['uid']) == users[1]
        await repository.update(uid=users[1]['uid'])
        assert await repository.get_one(uid=users[1]['uid']) == users[1]
        await repository.update(new_uid='100000000')
        assert await repository.get_one(uid='100000000') is None  # no update is performed without input data

        await repository.update(uid=users[1]['uid'], new_snp='1 2 3')
        assert await repository.get_one(snp='1 2 3') is not None  # updating by uid

        await repository.update(snp='1 2 3', new_phone='1 2 3 4')
        assert await repository.get_one(phone='1 2 3 4') is not None  # updating by snp

        await repository.update(phone='1 2 3 4', new_is_admin=not users[1]['is_admin'])
        assert (await repository.get_one(phone='1 2 3 4'))['is_admin'] == (not users[1]['is_admin'])  # updating by phone

        await repository.update(phone='1 2 3 4', is_admin=not users[1]['is_admin'], new_tg_chat_id=0)
        assert await repository.get_one(tg_chat_id=0) is not None  # updating by is_admin

        await repository.update(tg_chat_id=0, new_uid='1 2')
        assert await repository.get_one(uid='1 2') is not None  # updating by tg_chat_id

        assert await repository.get_one(uid=old_uid) is None  # data changes, not new ones are created
        del old_uid

        # does not delete non-existent elements and does not throw exceptions
        old_number = len(await repository.get_all())
        await repository.delete(uid='123')  # no exceptions
        assert old_number == len(await repository.get_all())  # the number of elements has not changed
        del old_number

        # deletes by parameter
        assert await repository.add(users[1]) == users[1]
        assert await repository.get_one(uid=users[1]['uid']) is not None  # element exists
        await repository.delete(uid=users[1]['uid'])  # no exceptions
        assert await repository.get_one(uid=users[1]['uid']) is None  # element deleted

        await repository.add(users[1])
        assert await repository.get_one(snp=users[1]['snp']) is not None  # element exists
        await repository.delete(snp=users[1]['snp'])  # no exceptions
        assert await repository.get_one(snp=users[1]['snp']) is None  # element deleted

        await repository.add(users[1])
        assert await repository.get_one(phone=users[1]['phone']) is not None  # element exists
        await repository.delete(phone=users[1]['phone'])  # no exceptions
        assert await repository.get_one(phone=users[1]['phone']) is None  # element deleted

        await repository.add(users[1])
        assert await repository.get_one(is_admin=users[1]['is_admin'], phone=users[1]['phone']) is not None  # element exists
        await repository.delete(is_admin=users[1]['is_admin'], phone=users[1]['phone'])  # no exceptions
        assert await repository.get_one(is_admin=users[1]['is_admin'], phone=users[1]['phone']) is None  # element deleted

        await repository.add(users[1])
        assert await repository.get_one(tg_chat_id=users[1]['tg_chat_id']) is not None  # element exists
        await repository.delete(tg_chat_id=users[1]['tg_chat_id'])  # no exceptions
        assert await repository.get_one(tg_chat_id=users[1]['tg_chat_id']) is None  # element deleted

        # return of modified data
        await repository.delete()
        await repository.add(users)

        # close session
        await session.close()

    print('---------FINISH INTERACTION WITH USERS--------\n')
