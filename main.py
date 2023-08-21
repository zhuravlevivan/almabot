import os

from aiogram.utils import executor
from create_bot import dp
from handlers import user, admin, other
from database import sqlite_db


async def on_startup(_):
    print('Bot Online')
    sqlite_db.sql_start()
    # print(os.getenv('ADMINS'))

user.register_handlers_user(dp)
admin.register_handlers_admin(dp)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
