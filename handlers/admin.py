import uuid

from aiogram import types, Dispatcher
from create_bot import bot, os
import config
from keyboards.admin_kb import admin_access_kb


async def admin_cmd(message: types.Message):
    if message.chat.id in config.ADMINS:
        await bot.send_message(message.chat.id, "[--------A-C-C-E-S-S---Z-O-N-E--------]", reply_markup=admin_access_kb)
    else:
        await bot.send_message(message.chat.id, "Вы не админ")


# async def remove_cmd(message):
# async def rename_cmd(message):
# async def getfile_cmd(message):
# async def users_cmd(message):


# async def voice_processing(message):
#     if message.chat.id in config.ADMINS:
#         try:
#             file_name = str(uuid.uuid4())[:8]
#             file_info = bot.get_file(message.voice.file_id)
#             downloaded_file = bot.download_file(file_info.file_path)
#             with open(os.path.join('files/', f'{file_name}.ogg'), 'wb') as new_file:
#                 new_file.write(downloaded_file)
#
#             cur.execute(f"INSERT INTO lections(path) VALUES (?)", [f'{file_name}.ogg'])
#             conn.commit()
#             bot.reply_to(message, f"Сохранено с именем {file_name}.ogg!")
#         except Exception as e:
#             bot.reply_to(message, e)
#     else:
#         bot.send_message(message.chat.id, "Вам нельзя!")


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(admin_cmd, commands=['admin'])
    # dp.register_callback_query_handler(query_handler)


# ------------- INLINE KB QUERY START ------------- #
# async def query_handler(callback: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query_id=callback.id)
#     answer = ''
#     if callback.data == '1':
#         answer = '[--------A-C-C-E-S-S---Z-O-N-E--------]'
#         await bot.send_message(chat_id=callback.from_user.id,
#                                text="[--------A-C-C-E-S-S---Z-O-N-E--------]",
#                                reply_markup=admin_access_kb)
#
#     await bot.send_message(callback.message.chat.id, answer)
#     await bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id)
# ------------- INLINE KB QUERY END ------------- #
