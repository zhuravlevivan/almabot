from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

b1 = KeyboardButton('/files')
b2 = KeyboardButton('/getfile')

user_kb = ReplyKeyboardMarkup(one_time_keyboard=True)

user_kb.row(b1, b2)
