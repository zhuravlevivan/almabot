from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import BotCommand
from TEXTS import COMMANDS

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
arb2 = KeyboardButton('users')
arb3 = KeyboardButton('remove')
arb4 = KeyboardButton('rename')
arb5 = KeyboardButton('files')
arb6 = KeyboardButton('getfile')
arb7 = KeyboardButton('caption')


admin_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
admin_menu_kb.row(arb1, arb2)
admin_menu_kb.row(arb3, arb4, arb5)
admin_menu_kb.row(arb6, arb7)


# ------------ MENU KB END ------------ #

# ------------ CANCEL KB START ------------ #
cm_kb1 = KeyboardButton('cancel')

cancel_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
cancel_menu_kb.row(cm_kb1)
# ------------ CANCEL KB END ------------ #

# ------------ ACCESS REPLY KB START ------------ #
admin_access_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Cancel '
                                                                                                            'available')

akb1 = KeyboardButton('give_accept')
akb2 = KeyboardButton('del_accept')
akb3 = KeyboardButton('show_acc')
akb4 = KeyboardButton('del_user')

akb5 = KeyboardButton('mailing')
akb6 = KeyboardButton('backup')
akb7 = KeyboardButton('go_back')
admin_access_kb.row(akb1, akb2, akb3)
admin_access_kb.row(akb4, akb5, akb6)
admin_access_kb.row(akb7)
# ------------ ACCESS REPLY KB END ------------ #


async def set_main_menu(bot: Bot):
    main_menu_commands = [BotCommand(
        command=command,
        description=description
    ) for command,
        description in COMMANDS.items()]
    await bot.set_my_commands(main_menu_commands)

# ------------ ACCESS INLINE KB START ------------ #
# admin_access_kb = InlineKeyboardMarkup(row_width=1)
#
# akb1 = KeyboardButton("Выдать доступ пользователю", callback_data='gaccept')
# akb2 = KeyboardButton("Забрать доступ у пользователя", callback_data='daccept')
# akb3 = KeyboardButton("Рассылка", callback_data='rass')
# admin_access_kb.add(akb3, akb1, akb2)
# ------------ ACCESS INLINE KB END ------------ #
