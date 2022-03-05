async def start(engine, base):
    print('---------------START TABLE DROPPING--------------')

    # drop all tables from the database
    async with engine.begin() as connection:
        await connection.run_sync(base.metadata.drop_all)

    print('--------------FINISH TABLE DROPPING--------------\n')
