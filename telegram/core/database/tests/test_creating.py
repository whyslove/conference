# from db_api.delete.phrases import elements as delete_phrases

from create_table import update_tables


async def start(SessionLocal):
    print('----------------START DB CREATING----------------')

    # all tables with dependencies exist or are being created
    async with SessionLocal() as session:
        assert await update_tables() == 0  # no exceptions

        # reset the database
        # assert await delete_phrases(session) == 0

        # close session
        await session.close()

    print('---------------FINISH DB CREATING----------------\n')
