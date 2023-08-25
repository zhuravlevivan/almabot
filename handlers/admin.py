from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from create_bot import os, bot
import config
from database import sqlite_db
from keyboards.admin_kb import admin_menu_kb, admin_access_kb, cancel_menu_kb
from keyboards.user_kb import user_kb
from datetime import datetime


# ------------- STATE CLASSES START ------------- #
class RenameFile(StatesGroup):
    OldName = State()  # Состояние ожидания старого имени файла
    NewName = State()  # Состояние ожидания нового имени файла


class RemoveFile(StatesGroup):
    FileRemoveName = State()  # Состояние ожидания имени файла


class RemoveUser(StatesGroup):
    UserIDTORemove = State()


class GetFile(StatesGroup):
    FileName = State()  # Состояние ожидания имени файла


class AccessToFilesStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_file_name = State()
    waiting_for_delete_user_id = State()
    waiting_for_delete_file_name = State()


class MailingState(StatesGroup):
    waiting_text_mailing = State()


# ------------- STATE CLASSES END ------------- #


def is_admin(message):
    return str(message.chat.id) in config.ADMINS


async def go_back(message: types.Message):
    if message.text == 'go_back' and is_admin(message):
        await message.answer('ok', reply_markup=admin_menu_kb)


# ------------- ADMIN CMD START ------------- #
async def admin_cmd(message: types.Message):
    if is_admin(message):
        await bot.send_message(message.chat.id, "[--------A-C-C-E-S-S---Z-O-N-E--------]", reply_markup=admin_access_kb)
    else:
        await bot.send_message(message.chat.id, "Вы не админ")


# ------------- ADMIN CMD END ------------- #


# ------------- RENAME CMD START ------------- #
async def rename_cmd(message: types.Message):
    if is_admin(message):
        await message.answer("Введите старое имя файла:", reply_markup=cancel_menu_kb)
        await RenameFile.OldName.set()


# ---- STATE CANCEL START ------------ #

async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    if is_admin(message):
        await message.reply('ok', reply_markup=admin_menu_kb)
    else:
        await message.reply('ok', reply_markup=user_kb)


# ---- STATE CANCEL END ------------ #

# ------------- RENAME CMD START ------------- #
async def process_old_name_step(message: types.Message, state: FSMContext):

    old_name = message.text
    if old_name in os.listdir('files/'):
        await message.answer("Введите новое имя файла:")
        await state.update_data(old_name=old_name)
        await RenameFile.NewName.set()
    else:
        await message.answer("Файл с таким именем не найден", reply_markup=admin_menu_kb)
        await state.finish()


async def process_new_name_step(message: types.Message, state: FSMContext):
    new_name = message.text
    data = await state.get_data()
    old_name = data.get('old_name')

    try:
        sqlite_db.cur.execute(f"UPDATE lections SET path = '{new_name}' WHERE path = '{old_name}'")
        sqlite_db.cur.execute(f"UPDATE access SET alectionid = '{new_name}' WHERE alectionid = '{old_name}'")
        sqlite_db.base.commit()
        os.rename(os.path.join('files/', f'{old_name}'), os.path.join('files/', f'{new_name}'))
        await message.answer(f"Файл успешно переименован в {new_name}", reply_markup=admin_menu_kb)

    except Exception as e:
        await message.answer(f"Ошибка при переименовании файла: {e}", reply_markup=admin_menu_kb)

    await state.finish()


# ------------- RENAME CMD END ------------- #


# ------------- REMOVE CMD START ------------- #
async def remove_cmd(message: types.Message):
    if is_admin(message):
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


# ------------- REMOVE USER START ------------- #
async def remove_user_cmd(message: types.Message):
    if is_admin(message):
        await message.answer("Введите ID пользователя:", reply_markup=cancel_menu_kb)
        await RemoveUser.UserIDTORemove.set()


async def process_remove_user_step(message: types.Message, state: FSMContext):
    # noinspection PyBroadException
    user_id = message.text
    # Сохранение ID пользователя в контексте FSM
    if user_id in await sqlite_db.users_list(message):
        try:
            sqlite_db.cur.execute(f'DELETE FROM users WHERE chatid = "{message.text}"')
            sqlite_db.cur.execute(f'DELETE FROM access WHERE auserid = "{message.text}"')
            sqlite_db.base.commit()
            await message.answer("Пользователь удален", reply_markup=admin_menu_kb)
        except Exception as e:
            await message.answer(f"Ошибка при удалении: {e}", reply_markup=admin_menu_kb)
    else:
        await message.answer("Пользователь не найден", reply_markup=admin_menu_kb)
        await state.finish()
    await state.finish()


# ------------- REMOVE USER END ------------- #


# ------------- USERS CMD START ------------- #
async def users_cmd(message: types.Message):
    if is_admin(message):
        await sqlite_db.show_users(message)


# ------------- USERS CMD END ------------- #


# ------------- GETFILE START ------------- #
async def get_file(message: types.Message):
    sqlite_db.cur.execute(f"SELECT auserid FROM access WHERE auserid = '{message.chat.id}'")
    result = sqlite_db.cur.fetchall()
    try:
        if len(result) == 0:
            await message.answer("Нет доступа...")
        else:
            await message.answer("Введите название файла:")
            await GetFile.FileName.set()
    except Exception as e:
        await message.answer(str(e))


async def process_get_file(message: types.Message, state: FSMContext):
    # noinspection PyBroadException
    user_id = message.chat.id
    file_name = message.text
    if file_name in os.listdir('files/'):
        sqlite_db.cur.execute(
            f"SELECT * FROM access WHERE auserid = {user_id} AND alectionid = '{file_name}'")
        if len(sqlite_db.cur.fetchall()) == 0:
            await message.answer('Доступ еще не предоставлен')
        else:
            doc = open(f'files/{file_name}', 'rb')
            try:
                await bot.send_audio(user_id, doc,
                                     protect_content=True,
                                     caption="{SOME TEXT}")

            except Exception as e:
                await bot.send_message(user_id, str(e))

            doc.close()
    else:
        await message.answer('Файл не найден')

    await state.finish()


# ------------- GETFILE END ------------- #


# ------------- GIVING ACCESS START ------------- #

async def giving_access(message: types.Message):
    if is_admin(message):
        await message.answer("Введите ID пользователя:", reply_markup=cancel_menu_kb)
        await AccessToFilesStates.waiting_for_user_id.set()


async def process_user_id(message: types.Message, state: FSMContext):
    user_id = message.text
    # Сохранение ID пользователя в контексте FSM
    if user_id.isdigit() and user_id in await sqlite_db.users_list(message):
        await state.update_data(user_id=user_id)
        await message.answer("Введите название файла:", reply_markup=cancel_menu_kb)
        await AccessToFilesStates.waiting_for_file_name.set()
    else:
        await message.reply("ID не найден", reply_markup=admin_menu_kb)
        await state.finish()


async def process_file_name(message: types.Message, state: FSMContext):
    lecture = message.text
    data = await state.get_data()
    user_id = data.get("user_id")
    # Проверка наличия файла в базе данных по имени
    if lecture in os.listdir('files/'):
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


# ------------- DELETE ACCESS START ------------- #

async def delete_access(message: types.Message):
    if is_admin(message):
        await message.answer("Введите ID пользователя:", reply_markup=cancel_menu_kb)
        await AccessToFilesStates.waiting_for_delete_user_id.set()


async def process_delete_user_id(message: types.Message, state: FSMContext):
    user_id = message.text
    # Сохранение ID пользователя в контексте FSM
    if user_id.isdigit() and user_id in await sqlite_db.users_list(message):
        await state.update_data(user_id=user_id)
        await message.answer("Введите название файла:", reply_markup=cancel_menu_kb)
        await AccessToFilesStates.waiting_for_delete_file_name.set()
    else:
        await message.reply("ID не найден", reply_markup=admin_menu_kb)
        await state.finish()


async def process_delete_file_name(message: types.Message, state: FSMContext):
    lecture = message.text
    data = await state.get_data()
    user_id = data.get("user_id")
    # Проверка наличия файла в базе данных по имени
    if lecture in os.listdir('files/'):
        sqlite_db.cur.execute(
            f"SELECT * FROM access WHERE auserid = '{user_id}'"
            f"AND alectionid = '{lecture}'"
        )
        if sqlite_db.cur.fetchone() is None:
            await message.answer("Доступ уже отозван", reply_markup=admin_menu_kb)
        else:
            sqlite_db.cur.execute(f"DELETE FROM access WHERE auserid = '{user_id}'"
                                  f"AND alectionid = '{lecture}'",
                                  )
            sqlite_db.base.commit()
            await message.answer(f"Успешно! отозвали доступ у - {user_id} "
                                 f"к файлу {lecture}", reply_markup=admin_menu_kb)
    else:
        await message.reply("Файл с таким именем не найден", reply_markup=admin_menu_kb)

    # Сброс состояния FSM
    await state.finish()


# ------------- DELETE ACCESS END ------------- #

# ------------- MAILING START ------------- #
async def mailing(message: types.Message):
    if is_admin(message):
        await message.answer("Введите текст рассылки:", reply_markup=cancel_menu_kb)
        await MailingState.waiting_text_mailing.set()


async def process_text_mailing(message: types.Message, state: FSMContext):
    # noinspection PyBroadException
    txt = message.text
    sqlite_db.cur.execute(f"SELECT chatid FROM users")
    mailing_baza = sqlite_db.cur.fetchall()
    for user in range(len(mailing_baza)):
        try:
            await bot.send_message(mailing_baza[user][0], txt)
        except Exception as e:
            await message.answer(str(e))
    await message.answer('Рассылка завершена', reply_markup=admin_menu_kb)

    await state.finish()


# ------------- MAILING END ------------- #


# ------------- PROCESSING VOICE START ------------- #
async def voice_processing(message: types.Message):
    if is_admin(message):
        try:
            file_name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".ogg"

            await message.voice.download(destination_file=f"files/{file_name}")
            sqlite_db.cur.execute(f"INSERT INTO lections(path) VALUES (?)", [f'{file_name}'])
            sqlite_db.base.commit()
            await message.reply(f"Сохранено с именем {file_name}")
        except Exception as e:
            await message.reply(str(e))
    else:
        await message.reply("Вам нельзя!")


# ------------- PROCESSING VOICE END ------------- #


# ------------- PROCESSING SAVE AUDIO START ------------- #
async def handle_audio_or_document(message: types.Message):
    if is_admin(message):
        try:
            if message.audio:
                file_info = await bot.get_file(message.audio.file_id)
                downloaded_file = await bot.download_file(file_info.file_path)
                src = 'files/' + message.audio.file_name
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file.getvalue())

                sqlite_db.cur.execute(f"INSERT INTO lections(path) VALUES (?)", [message.audio.file_name])
                sqlite_db.base.commit()

                await message.answer(f'Успешно сохранено\n Имя файла: {message.audio.file_name}!')
            elif message.document:
                file_info = await bot.get_file(message.document.file_id)
                downloaded_file = await bot.download_file(file_info.file_path)
                src = 'files/' + message.document.file_name
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file.getvalue())

                sqlite_db.cur.execute(f"INSERT INTO lections(path) VALUES (?)", [message.audio.file_name])
                sqlite_db.base.commit()

                await message.answer(f'Успешно сохранено\n Имя файла: {message.document.file_name}!')

        except Exception as e:
            await message.answer(str(e))
    else:
        await message.answer('Вам нельзя!')


# ------------- PROCESSING SAVE AUDIO END ------------- #

# ------------- HANDLER REGISTRATIONS START ------------- #
# def register_handlers_admin(dp: Dispatcher):
#     dp.register_message_handler(admin_cmd, Text(equals='admin', ignore_case=True))
#
#     dp.register_message_handler(rename_cmd, Text(equals='rename', ignore_case=True), state=None)
#     dp.register_message_handler(cancel_handler, Text(equals='cancel', ignore_case=True), state='*')
#     dp.register_message_handler(process_old_name_step, state=RenameFile.OldName)
#     dp.register_message_handler(process_new_name_step, state=RenameFile.NewName)
#
#     dp.register_message_handler(users_cmd, Text(equals='users', ignore_case=True))
#
#     dp.register_message_handler(remove_cmd, Text(equals='remove', ignore_case=True), state=None)
#     dp.register_message_handler(process_file_remove_step, state=RemoveFile.FileRemoveName)
#
#     dp.register_message_handler(giving_access, Text(equals='give_accept', ignore_case=True))
#     dp.register_message_handler(process_user_id, state=AccessToFilesStates.waiting_for_user_id)
#     dp.register_message_handler(process_file_name, state=AccessToFilesStates.waiting_for_file_name)
#
#     dp.register_message_handler(delete_access, Text(equals='del_accept', ignore_case=True))
#     dp.register_message_handler(process_delete_user_id, state=AccessToFilesStates.waiting_for_delete_user_id)
#     dp.register_message_handler(process_delete_file_name, state=AccessToFilesStates.waiting_for_delete_file_name)
#
#     dp.register_message_handler(go_back, Text(equals='go_back', ignore_case=True))
#
#     dp.register_message_handler(mailing, Text(equals='mailing', ignore_case=True))
#     dp.register_message_handler(process_text_mailing, state=MailingState.waiting_text_mailing)
#
#     dp.register_message_handler(get_file, Text(equals='getfile', ignore_case=True))
#     dp.register_message_handler(process_get_file, state=GetFile.FileName)
#
#     dp.register_message_handler(voice_processing, content_types=types.ContentType.VOICE)
#     dp.register_message_handler(handle_audio_or_document, content_types=[types.ContentType.AUDIO,
#                                                                          types.ContentType.DOCUMENT])

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
