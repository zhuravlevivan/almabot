from aiogram.utils import executor
from create_bot import dp
from handlers import user, admin, other



async def on_startup(_):
    print('Bot Online')


user.register_handlers_user(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
