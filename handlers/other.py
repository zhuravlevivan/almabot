# import config
# from database.sqlite_db import sq
# from aiogram import types
# from aiogram.types import CallbackQuery, Message
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from create_bot import bot
# from keyboards import user_kb, admin_menu_kb
# from aiogram.dispatcher.filters import Text
# from aiogram import Dispatcher
#
#
# async def show_all_users(message: types.Message):
#     global base, cur
#     base = sq.connect('C:\\Users\\ZhuravlevIV\\OneDrive\\Рабочий стол\\Bot_Kate\\botlzt_upd\\users__.db',
#                       check_same_thread=False)
#     cur = base.cursor()
#     user_list = []
#     i = 0
#     for value in cur.execute(f"SELECT * FROM users").fetchall():
#         user_list.append(f"{i} {value[0]} {value[2]}")
#         i += 1
#
#     page = 2
#     items_per_page = 10
#     index = items_per_page * page
#
#     for user in user_list[index - 10:index]:
#         print(user)
#
#     # print('\n'.join(user_list))
#
#     # await message.answer('\n'.join(user_list))
#
#
# async def process_forward_press(callback: CallbackQuery):
#     pass
