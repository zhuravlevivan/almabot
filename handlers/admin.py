from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from create_bot import bot, os
import config
from database import sqlite_db
from keyboards.admin_kb import admin_menu_kb, admin_access_kb, cancel_menu_kb
from datetime import datetime


# ------------- STATE CLASSES START ------------- #
class RenameFile(StatesGroup):
    OldName = State()  # Состояние ожидания старого имени файла
    NewName = State()  # Состояние ожидания нового имени файла


class RemoveFile(StatesGroup):
    FileRemoveName = State()  # Состояние ожидания имени файла


class GetFile(StatesGroup):
    FileName = State()  # Состояние ожидания имени файла


class AccessToFilesStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_file_name = State()


# ------------- STATE CLASSES END ------------- #


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
        sqlite_db.cur.execute(f"UPDATE lections SET path = '{new_name}' WHERE path = '{old_name}'")
        sqlite_db.base.commit()
        os.rename(os.path.join('files/', f'{old_name}'), os.path.join('files/', f'{new_name}'))
        await message.answer(f"Файл успешно переименован в {new_name}", reply_markup=admin_menu_kb)

    except Exception as e:
        await message.answer(f"Ошибка при переименовании файла: {e}", reply_markup=admin_menu_kb)

    await state.finish()


# ------------- RENAME CMD END ------------- #


# ------------- REMOVE CMD START ------------- #
async def remove_cmd(message: types.Message):
    if message.chat.id in config.ADMINS:
        await message.answer("Введите имя файла с расширением:", reply_markup=cancel_menu_kb)
        await RemoveFile.FileRemoveName.set()


async def process_file_remove_step(message: types.Message, state: FSMContext):
    # noinspection PyBroadException
    try:
        os.remove(f'files/{message.text}')
        sqlite_db.cur.execute(f'DELETE FROM lections WHERE path = "{message.text}"')
        sqlite_db.cur.execute(f'DELETE FROM access WHERE alectionid = "{message.text}"')
        sqlite_db.base.commit()
        await message.answer("Файл удален", reply_markup=admin_menu_kb)

    except OSError as e:
        await message.answer(f"Ошибка при удалении файла: {e.strerror}", reply_markup=admin_menu_kb)

    await state.finish()


# ------------- REMOVE CMD END ------------- #


# ------------- GETFILE CMD START ------------- #
# async def getfile_cmd(message: types.Message):
#     sqlite_db.cur.execute(f"SELECT auserid FROM access WHERE auserid = '{message.chat.id}'")
#     result = sqlite_db.cur.fetchall()
#     if len(result) > 0:
#         try:
#             if message.chat.id not in (result[0]):
#                 bot.send_message(message.chat.id, "Нет доступа...")
#             else:
#                 await message.answer("Введите имя файла с расширением:", reply_markup=cancel_menu_kb)
#                 await GetFile.FileName.set()
#         except Exception as e:
#             await message.answer(str(e))
#     else:
#         await message.answer("Некому выдавать доступ")
#
#
# async def process_get_file_access_step(message: types.Message, state: FSMContext):
#     files = os.listdir('files/')
#     if message.text in files:
#         try:
#             # sqlite_db.cur.execute(f"SELECT * FROM access WHERE auserid = '{message.from_user.id}' AND alectionid = '{message.text}'")
#             print(f"SELECT * FROM access WHERE auserid = '{message.from_user.id}' AND alectionid = '{message.text}'")
#         except Exception as e:
#             await message.answer(str(e))
#
#     await state.finish()

#  *******************************************************************
# ------------- GETFILE CMD END ------------- #


# ------------- USERS CMD START ------------- #
async def users_cmd(message: types.Message):
    await sqlite_db.show_users(message)


# ------------- USERS CMD END ------------- #


# ------------- GIVING ACCESS START ------------- #
async def giving_access(message: types.Message):
    await message.answer("Введите ID пользователя:", reply_markup=cancel_menu_kb)
    await AccessToFilesStates.waiting_for_user_id.set()


async def process_user_id(message: types.Message, state: FSMContext):
    user_id = message.text
    # Сохранение ID пользователя в контексте FSM
    if user_id.isdigit():
        await state.update_data(user_id=user_id)
        await message.answer("Введите название файла:", reply_markup=cancel_menu_kb)
        await AccessToFilesStates.waiting_for_file_name.set()
    else:
        await message.reply("Это не ID", reply_markup=admin_menu_kb)
        await state.finish()


async def process_file_name(message: types.Message, state: FSMContext):
    lecture = message.text
    data = await state.get_data()
    user_id = data.get("user_id")
    # Проверка наличия файла в базе данных по имени
    if lecture in config.FILES:
        sqlite_db.cur.execute(
            f"SELECT * FROM access WHERE auserid = '{user_id}'"
            f"AND alectionid = '{lecture}'"
        )
        if sqlite_db.cur.fetchone() is None:
            sqlite_db.cur.execute(f"INSERT INTO access VALUES (?,?)",
                                  (f'{user_id}',
                                   f'{lecture}')
                                  )
            sqlite_db.base.commit()
            await bot.send_message(message.chat.id, f"Успешно! Выдали доступ - {user_id} "
                                             
                                                    f"к файлу {lecture}", reply_markup=admin_menu_kb)
        else:
            await message.reply("Доступ уже выдан", reply_markup=admin_menu_kb)
    else:
        await message.reply("Файл с таким именем не найден", reply_markup=admin_menu_kb)

    # Сброс состояния FSM
    await state.finish()


# ------------- GIVING ACCESS END ------------- #


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
    dp.register_message_handler(remove_cmd, commands=['remove'], state=None)
    dp.register_message_handler(process_file_remove_step, state=RemoveFile.FileRemoveName)
    # dp.register_message_handler(getfile_cmd, commands=['getfile'])
    # dp.register_message_handler(process_get_file_access_step, state=GetFile.FileName)
    # dp.register_message_handler(cancel_handler, Text(equals='cancel', ignore_case=True), state='*')
    dp.register_message_handler(giving_access, Text(equals='gaccept', ignore_case=True))
    dp.register_message_handler(process_user_id, state=AccessToFilesStates.waiting_for_user_id)
    dp.register_message_handler(process_file_name, state=AccessToFilesStates.waiting_for_file_name)
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
