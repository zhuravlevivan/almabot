from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from create_bot import bot

mkb1 = InlineKeyboardButton(text='admin', callback_data='1')
mkb2 = InlineKeyboardButton(text='files', callback_data='2')
mkb3 = InlineKeyboardButton(text='remove', callback_data='3')
mkb4 = InlineKeyboardButton(text='rename', callback_data='4')
mkb5 = InlineKeyboardButton(text='users', callback_data='5')
mkb6 = InlineKeyboardButton(text='getfile', callback_data='6')

admin_menu_kb = InlineKeyboardMarkup()

admin_menu_kb.row(mkb1, mkb2, mkb3)
admin_menu_kb.row(mkb4, mkb5, mkb6)




admin_access_kb = InlineKeyboardMarkup(row_width=1)

akb1 = KeyboardButton("Выдать доступ пользователю", callback_data='gaccept')
akb2 = KeyboardButton("Забрать доступ у пользователя", callback_data='daccept')
akb3 = KeyboardButton("Рассылка", callback_data='rass')
admin_access_kb.add(akb3, akb1, akb2)
