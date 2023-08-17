from aiogram import types, Dispatcher
from create_bot import bot
import config
from keyboards.admin_kb import admin_access_kb


# async def admin_cmd(message: types.Message):
#     if message.chat.id in config.ADMINS:
#         if message.text == 'admin':
#             await message.reply("Вы успешно залогинились в админку!", reply_markup=admin_access_kb)
#     else:
#         await message.reply("Вы не админ")


# async def send_text(message: types.Message):
#     if message.text.lower() == 'admin':
#         await message.reply("Вы успешно залогинились в админку!", reply_markup=admin_access_kb)


async def query_handler(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback_query_id=callback.id)
    answer = ''
    if callback.data == '1':
        answer = '[--------A-C-C-E-S-S---Z-O-N-E--------]'
        await bot.send_message(chat_id=callback.from_user.id,
                               text="[--------A-C-C-E-S-S---Z-O-N-E--------]",
                               reply_markup=admin_access_kb)

    await bot.send_message(callback.message.chat.id, answer)
    await bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id)


def register_handlers_admin(dp: Dispatcher):
    # dp.register_message_handler(send_text)
    dp.register_callback_query_handler(query_handler)
