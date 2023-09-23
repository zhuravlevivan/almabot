import asyncio

from aiogram.utils import executor
from config import dp, bot
from handlers import register_mh
from database import sqlite_db, backup_db_script
from keyboards.admin_kb import set_main_menu


async def on_startup(_):
    print('Bot Online')
    await set_main_menu(bot)
    sqlite_db.sql_start()

    # loop = asyncio.get_event_loop()
    loop.create_task(backup_db_script.scheduled_function())


register_mh.register_handlers_user(dp)
register_mh.register_handlers_admin(dp)

if __name__ == '__main__':
    # executor.start_polling(dp,  skip_updates=True, on_startup=on_startup)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(on_startup(None))
    executor.start_polling(dp,  skip_updates=True)
