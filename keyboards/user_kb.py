from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

b1 = KeyboardButton('files')
b2 = KeyboardButton('getfile')

user_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

user_kb.row(b1, b2)
