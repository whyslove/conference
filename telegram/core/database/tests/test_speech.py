from datetime import datetime

from tests.test_data import speeches

from repositories.speech import SpeechRepository


async def start(SessionLocal):
    print('----------START INTERACTION WITH SPEECHES---------')

    async with SessionLocal() as session:
        repository = SpeechRepository(session)

        # adding items does not throw exceptions
        await repository.add(speeches)  # no exceptions

        speeches[0]['key'] = 'own key'

        try:
            await repository.add(speeches)
        except Exception as e:
            assert type(e) == ValueError
        else:
            assert False
        speeches[0]['key'] = 'own key2'

        # updating all data for all parameters does not throw exceptions
        old_key = speeches[1]['key']
        await repository.update()  # empty query throws no exceptions
        # updating zero amount of data does not change the item
        assert await repository.get_one(key=speeches[1]['key']) == speeches[1]
        await repository.update(key=speeches[1]['key'])
        assert await repository.get_one(key=speeches[1]['key']) == speeches[1]
        await repository.update(new_key='100000000')
        assert await repository.get_one(key='100000000') is None  # no update is performed without input data

        await repository.update(key=speeches[1]['key'], new_title='new_t')
        assert await repository.get_one(title='new_t') is not None  # updating by key

        new_start_time = datetime.now()
        await repository.update(title='new_t', new_start_time=new_start_time)
        assert await repository.get_one(start_time=new_start_time) is not None  # updating by title

        new_end_time = datetime.now()
        await repository.update(start_time=new_start_time, new_end_time=new_end_time)
        assert await repository.get_one(end_time=new_end_time) is not None  # updating by start_time

        await repository.update(end_time=new_end_time, new_venue='new_v')
        assert await repository.get_one(venue='new_v') is not None  # updating by end_time
        del new_start_time, new_end_time

        await repository.update(venue='new_v', new_venue_description='new_v-d')
        assert await repository.get_one(venue_description='new_v-d') is not None  # updating by venue

        await repository.update(venue_description='new_v-d', new_key='1 2')
        assert await repository.get_one(key='1 2') is not None  # updating by venue_description

        assert await repository.get_one(key=old_key) is None  # data changes, not new ones are created
        del old_key

        # does not delete non-existent elements and does not throw exceptions
        old_number = len(await repository.get_all())
        await repository.delete(key='123')  # no exceptions
        assert old_number == len(await repository.get_all())  # the number of elements has not changed
        del old_number

        # deletes by parameter
        await repository.add(speeches[1])
        assert await repository.get_one(key=speeches[1]['key']) is not None  # element exists
        await repository.delete(key=speeches[1]['key'])  # no exceptions
        assert await repository.get_one(key=speeches[1]['key']) is None  # element deleted

        assert await repository.add(speeches[1]) == speeches[1]
        assert await repository.get_one(title=speeches[1]['title']) is not None  # element exists
        await repository.delete(title=speeches[1]['title'])  # no exceptions
        assert await repository.get_one(title=speeches[1]['title']) is None  # element deleted

        await repository.add(speeches[1])
        assert await repository.get_one(start_time=speeches[1]['start_time']) is not None  # element exists
        await repository.delete(start_time=speeches[1]['start_time'])  # no exceptions
        assert await repository.get_one(start_time=speeches[1]['start_time']) is None  # element deleted

        await repository.add(speeches[1])
        assert await repository.get_one(end_time=speeches[1]['end_time']) is not None  # element exists
        await repository.delete(end_time=speeches[1]['end_time'])  # no exceptions
        assert await repository.get_one(end_time=speeches[1]['end_time']) is None  # element deleted

        await repository.add(speeches[1])
        assert await repository.get_one(venue=speeches[1]['venue']) is not None  # element exists
        await repository.delete(venue=speeches[1]['venue'])  # no exceptions
        assert await repository.get_one(venue=speeches[1]['venue']) is None  # element deleted

        await repository.add(speeches[1])
        assert await repository.get_one(venue_description=speeches[1]['venue_description']) is not None  # element exists
        await repository.delete(venue_description=speeches[1]['venue_description'])  # no exceptions
        assert await repository.get_one(venue_description=speeches[1]['venue_description']) is None  # element deleted

        # return of modified data
        await repository.delete()
        await repository.add(speeches)

        # close session
        await session.close()

    print('---------FINISH INTERACTION WITH SPEECHES---------\n')
