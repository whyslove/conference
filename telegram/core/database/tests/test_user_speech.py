from tests.test_data import user_speeches, speeches, users, roles

from repositories.user_speech import UserSpeechRepository


async def start(SessionLocal):
    print('----------START INTERACTION WITH USER_SPEECHES---------')

    async with SessionLocal() as session:
        repository = UserSpeechRepository(session)

        # adding items does not throw exceptions
        await repository.add(user_speeches)  # no exceptions

        try:
            await repository.add(user_speeches)
        except Exception as e:
            assert type(e) == ValueError
        else:
            assert False

        # updating all data for all parameters does not throw exceptions
        old_uid = user_speeches[1]['uid']
        old_key = user_speeches[1]['key']

        await repository.update()  # empty query throws no exceptions
        # updating zero amount of data does not change the item
        assert await repository.get_one(
            uid=user_speeches[1]['uid'], key=user_speeches[1]['key']
        ) == user_speeches[1]
        await repository.update(uid=user_speeches[1]['uid'], key=user_speeches[1]['key'])
        assert await repository.get_one(
            uid=user_speeches[1]['uid'], key=user_speeches[1]['key']
        ) == user_speeches[1]
        await repository.update(new_uid='100000000')
        assert await repository.get_one(uid='100000000') is None  # no update is performed without input data

        await repository.update(uid=old_uid, key=old_key, new_role=roles[1]['value'])
        assert await repository.get_one(
            uid=old_uid,
            key=old_key,
            role=roles[1]['value']
        ) is not None  # updating by uid and key

        await repository.update(uid=old_uid, key=old_key, role=roles[1]['value'],
                                new_acknowledgment='1 2 3 4')
        assert await repository.get_one(acknowledgment='1 2 3 4') is not None  # updating by role

        await repository.update(acknowledgment='1 2 3 4',
                                new_uid=users[37]['uid'], new_key=speeches[72]['key'])
        assert await repository.get_one(uid=users[37]['uid'], key=speeches[72]['key']) is not None  # updating by acknowledgment

        assert await repository.get_one(uid=old_uid, key=old_key) is None  # data changes, not new ones are created
        await repository.update(acknowledgment='1 2 3 4', new_uid=old_uid)
        await repository.update(acknowledgment='1 2 3 4', new_key=old_key)
        assert await repository.get_one(uid=old_uid, key=old_key) is not None

        del old_uid
        del old_key

        # does not delete non-existent elements and does not throw exceptions
        old_number = len(await repository.get_all())
        await repository.delete(uid='123')  # no exceptions
        assert old_number == len(await repository.get_all())  # the number of elements has not changed
        del old_number

        user_speeches.append({
            'uid_key': f'{users[1]["uid"]}_{speeches[1]["key"]}',
            'uid': users[1]['uid'],
            'key': speeches[1]['key'],
            'role': roles[1]['value'],
            'acknowledgment': '123'
        })

        # deletes by parameter
        assert await repository.add(user_speeches[-1]) == user_speeches[-1]
        assert await repository.get_one(acknowledgment='123') is not None  # element exists
        await repository.delete(uid=user_speeches[-1]['uid'])  # no exceptions
        assert await repository.get_one(acknowledgment='123') is None  # element deleted

        await repository.add(user_speeches[-1])
        assert await repository.get_one(acknowledgment='123') is not None  # element exists
        await repository.delete(key=user_speeches[-1]['key'])  # no exceptions
        assert await repository.get_one(acknowledgment='123') is None  # element deleted

        await repository.add(user_speeches[-1])
        assert await repository.get_one(acknowledgment='123') is not None  # element exists
        await repository.delete(role=user_speeches[-1]['role'])  # no exceptions
        assert await repository.get_one(acknowledgment='123') is None  # element deleted

        await repository.add(user_speeches[-1])
        assert await repository.get_one(acknowledgment='123') is not None  # element exists
        await repository.delete(acknowledgment='123')  # no exceptions
        assert await repository.get_one(acknowledgment='123') is None  # element deleted

        # return of modified data
        user_speeches.pop()
        await repository.delete()
        await repository.add(user_speeches)

        # close session
        await session.close()

    print('---------FINISH INTERACTION WITH USER_SPEECHES--------\n')
