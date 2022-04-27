import asyncio
from core.database import create_table

async def run_init():
    await create_table.update_tables()
    # await set_token.set_token(config.settings.TOKEN)

if __name__ == "__main__":
    # uncomment to test all db functions
    asyncio.run(run_init())
