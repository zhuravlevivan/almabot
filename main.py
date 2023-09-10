from aiogram.utils import executor
from config import dp
from handlers import register_mh
from database import sqlite_db


async def on_startup(_):
    print('Bot Online')
    sqlite_db.sql_start()


register_mh.register_handlers_user(dp)
register_mh.register_handlers_admin(dp)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
