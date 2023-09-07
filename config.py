from environs import Env
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
storage = MemoryStorage()
env: Env = Env()
env.read_env()

# ADMINS = (101675480, 891528687, )
ADMINS = list(map(int, env.list('ADMINS')))
bot = Bot(token=env('TOKEN'))
dp = Dispatcher(bot, storage=storage)

