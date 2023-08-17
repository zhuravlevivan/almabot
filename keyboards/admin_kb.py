from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

b1 = KeyboardButton('/admin')
b2 = KeyboardButton('/files')
b3 = KeyboardButton('/rmfile')
b4 = KeyboardButton('/rename')
b5 = KeyboardButton('/users')
b6 = KeyboardButton('/getfile')

admin_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

admin_kb.row(b1, b2, b3)
admin_kb.row(b4, b5, b6)
