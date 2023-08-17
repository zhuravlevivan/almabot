import os

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
import dotenv

dotenv.load_dotenv()

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)
