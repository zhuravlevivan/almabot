from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from create_bot import bot, os
import config
from database import sqlite_db
from keyboards.admin_kb import admin_menu_kb, admin_access_kb, cancel_menu_kb
from datetime import datetime


class RenameFile(StatesGroup):
    OldName = State()  # Состояние ожидания старого имени файла
    NewName = State()  # Состояние ожидания нового имени файла


# ------------- ADMIN CMD START ------------- #

async def admin_cmd(message: types.Message):
    if message.chat.id in config.ADMINS:
        await bot.send_message(message.chat.id, "[--------A-C-C-E-S-S---Z-O-N-E--------]", reply_markup=admin_access_kb)
    else:
        await bot.send_message(message.chat.id, "Вы не админ")


# ------------- ADMIN CMD END ------------- #


# ------------- RENAME CMD START ------------- #
async def rename_cmd(message: types.Message):
    if message.chat.id in config.ADMINS:
        await message.answer("Введите старое имя файла:", reply_markup=cancel_menu_kb)
        await RenameFile.OldName.set()


# ------------ STATE CANCEL START ------------ #

async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('ok', reply_markup=admin_menu_kb)

# ------------ STATE CANCEL END ------------ #


async def process_old_name_step(message: types.Message, state: FSMContext):
    old_name = message.text

    await message.answer("Введите новое имя файла:")
    await state.update_data(old_name=old_name)
    await RenameFile.NewName.set()


async def process_new_name_step(message: types.Message, state: FSMContext):
    new_name = message.text
    data = await state.get_data()
    old_name = data.get('old_name')

    try:
        os.rename(os.path.join('files/', f'{old_name}'), os.path.join('files/', f'{new_name}'))
        await message.answer(f"Файл успешно переименован в {new_name}")

    except Exception as e:
        await message.answer(f"Ошибка при переименовании файла: {e}")

    await state.finish()


# ------------- RENAME CMD END ------------- #


# async def remove_cmd(message):
# async def rename_cmd(message):
# async def getfile_cmd(message):

async def users_cmd(message):
    await sqlite_db.show_users(message)


# ------------- PROCESSING VOICE START ------------- #
async def voice_processing(message: types.Message):
    if message.chat.id in config.ADMINS:
        try:
            file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".ogg"

            await message.voice.download(destination_file=f"files/{file_name}")
            sqlite_db.cur.execute(f"INSERT INTO lections(path) VALUES (?)", [f'{file_name}'])
            sqlite_db.base.commit()
            await message.reply(f"Сохранено с именем {file_name}")
        except Exception as e:
            await message.reply(str(e))
    else:
        await message.reply("Вам нельзя!")
# ------------- PROCESSING VOICE END ------------- #


# ------------- HANDLER REGISTRATIONS START ------------- #
def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(admin_cmd, commands=['admin'])
    dp.register_message_handler(rename_cmd, commands=['rename'], state=None)
    dp.register_message_handler(cancel_handler, state='*', commands='cancel')
    dp.register_message_handler(process_old_name_step, state=RenameFile.OldName)
    dp.register_message_handler(process_new_name_step, state=RenameFile.NewName)
    dp.register_message_handler(users_cmd, commands=['users'])
    dp.register_message_handler(voice_processing, content_types=types.ContentType.VOICE)
    # dp.register_message_handler(cancel_handler, Text(equals='cancel', ignore_case=True), state='*')
    # dp.register_callback_query_handler(query_handler)

# ------------- HANDLER REGISTRATIONS END ------------- #

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
