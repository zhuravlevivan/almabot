from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ------------ INLINE KB START ------------ #
# mkb1 = InlineKeyboardButton(text='admin', callback_data='1')
# mkb2 = InlineKeyboardButton(text='files', callback_data='2')
# mkb3 = InlineKeyboardButton(text='remove', callback_data='3')
# mkb4 = InlineKeyboardButton(text='rename', callback_data='4')
# mkb5 = InlineKeyboardButton(text='users', callback_data='5')
# mkb6 = InlineKeyboardButton(text='getfile', callback_data='6')
#
# admin_menu_kb = InlineKeyboardMarkup()
#
# admin_menu_kb.row(mkb1, mkb2, mkb3)
# admin_menu_kb.row(mkb4, mkb5, mkb6)
# ------------ INLINE KB END ------------ #

# ------------ MENU KB START ------------ #
arb1 = KeyboardButton('admin')
arb2 = KeyboardButton('files')
arb3 = KeyboardButton('remove')
arb4 = KeyboardButton('rename')
arb5 = KeyboardButton('users')
arb6 = KeyboardButton('getfile')


admin_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
admin_menu_kb.row(arb1, arb2, arb3)
admin_menu_kb.row(arb4, arb5, arb6)


# ------------ MENU KB END ------------ #

# ------------ CANCEL KB START ------------ #
cmkb1 = KeyboardButton('cancel')

cancel_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
cancel_menu_kb.row(cmkb1)
# ------------ CANCEL KB END ------------ #

# ------------ ACCESS REPLY KB START ------------ #
admin_access_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Cancel '
                                                                                                            'available')

akb1 = KeyboardButton('give_accept')
akb2 = KeyboardButton('del_accept')
akb3 = KeyboardButton('mailing')
akb5 = KeyboardButton('del_user')
akb4 = KeyboardButton('go_back')
admin_access_kb.add(akb3, akb1, akb2, akb5, akb4)
# ------------ ACCESS REPLY KB END ------------ #



# ------------ ACCESS INLINE KB START ------------ #
# admin_access_kb = InlineKeyboardMarkup(row_width=1)
#
# akb1 = KeyboardButton("Выдать доступ пользователю", callback_data='gaccept')
# akb2 = KeyboardButton("Забрать доступ у пользователя", callback_data='daccept')
# akb3 = KeyboardButton("Рассылка", callback_data='rass')
# admin_access_kb.add(akb3, akb1, akb2)
# ------------ ACCESS INLINE KB END ------------ #
