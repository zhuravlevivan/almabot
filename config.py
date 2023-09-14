from environs import Env
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()
env: Env = Env()
env.read_env()

ADMINS = list(map(int, env.list('ADMINS')))
bot = Bot(token=env('TOKEN'))
dp = Dispatcher(bot, storage=storage)

google_json = env('GOOGLE-SHEET-JSON')
tab_name = env('TAB-NAME')
folder_id = env('FOLDER-ID')
scope_gdrive = env('SCOPE-GDRIVE')
