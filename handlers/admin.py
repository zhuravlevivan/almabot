from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from create_bot import bot, os
import config
from handlers import other
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
    waiting_for_delete_user_id = State()
    waiting_for_delete_file_name = State()


class MailingState(StatesGroup):
    waiting_text_mailing = State()


# ------------- STATE CLASSES END ------------- #


def is_admin(message):
    return message.chat.id in config.ADMINS


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
    await message.reply('ok', reply_markup=admin_menu_kb)


# ---- STATE CANCEL END ------------ #

# ------------- RENAME CMD START ------------- #
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


# ------------- USERS CMD START ------------- #
async def users_cmd(message: types.Message):
    if is_admin(message):
        await sqlite_db.show_users(message)


# ------------- USERS CMD END ------------- #

# ------------- GETFILE START ------------- #
async def get_file(message: types.Message):
    if is_admin(message):
        sqlite_db.cur.execute(f"SELECT auserid FROM access WHERE auserid = '{message.chat.id}'")
        result = sqlite_db.cur.fetchall()
        # print(message.chat.id in result[0])
        try:
            if message.chat.id not in result[0]:
                await message.answer("Нет доступа...")
            else:
                await message.answer("Введите название файла:", reply_markup=cancel_menu_kb)
                await GetFile.FileName.set()
        except Exception as e:
            await message.answer(str(e), reply_markup=admin_menu_kb)


async def process_get_file(message: types.Message, state: FSMContext):
    # noinspection PyBroadException
    user_id = message.chat.id
    file_name = message.text
    print(file_name, file_name in config.FILES)
    if file_name in config.FILES:
        sqlite_db.cur.execute(
            f"SELECT * FROM access WHERE auserid = {user_id} AND alectionid = '{file_name}'")
        if sqlite_db.cur.fetchall() is None:
            await message.answer('Доступ еще не предоставлен')
        else:
            await other.sending_file(file_name, user_id)

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


# ------------- DELETE ACCESS START ------------- #

async def delete_access(message: types.Message):
    if is_admin(message):
        await message.answer("Введите ID пользователя:", reply_markup=cancel_menu_kb)
        await AccessToFilesStates.waiting_for_delete_user_id.set()


async def process_delete_user_id(message: types.Message, state: FSMContext):
    user_id = message.text
    # Сохранение ID пользователя в контексте FSM
    if user_id.isdigit():
        await state.update_data(user_id=user_id)
        await message.answer("Введите название файла:", reply_markup=cancel_menu_kb)
        await AccessToFilesStates.waiting_for_delete_file_name.set()
    else:
        await message.reply("Это не ID", reply_markup=admin_menu_kb)
        await state.finish()


async def process_delete_file_name(message: types.Message, state: FSMContext):
    lecture = message.text
    data = await state.get_data()
    user_id = data.get("user_id")
    # Проверка наличия файла в базе данных по имени
    print(lecture, user_id)
    if lecture in config.FILES:
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
    dp.register_message_handler(admin_cmd, Text(equals='admin'))
    dp.register_message_handler(rename_cmd, Text(equals='rename'), state=None)
    dp.register_message_handler(cancel_handler, Text(equals='cancel'), state='*')
    dp.register_message_handler(process_old_name_step, state=RenameFile.OldName)
    dp.register_message_handler(process_new_name_step, state=RenameFile.NewName)
    dp.register_message_handler(users_cmd, Text(equals='users'))
    dp.register_message_handler(voice_processing, content_types=types.ContentType.VOICE)
    dp.register_message_handler(remove_cmd, Text(equals='remove'), state=None)
    dp.register_message_handler(process_file_remove_step, state=RemoveFile.FileRemoveName)
    # dp.register_message_handler(getfile_cmd, commands=['getfile'])
    # dp.register_message_handler(process_get_file_access_step, state=GetFile.FileName)
    # dp.register_message_handler(cancel_handler, Text(equals='cancel', ignore_case=True), state='*')
    dp.register_message_handler(giving_access, Text(equals='give_accept', ignore_case=True))
    dp.register_message_handler(process_user_id, state=AccessToFilesStates.waiting_for_user_id)
    dp.register_message_handler(process_file_name, state=AccessToFilesStates.waiting_for_file_name)

    dp.register_message_handler(delete_access, Text(equals='delete_accept', ignore_case=True))
    dp.register_message_handler(process_delete_user_id, state=AccessToFilesStates.waiting_for_delete_user_id)
    dp.register_message_handler(process_delete_file_name, state=AccessToFilesStates.waiting_for_delete_file_name)
    dp.register_message_handler(go_back, Text(equals='go_back'))

    dp.register_message_handler(mailing, Text(equals='mailing'))
    dp.register_message_handler(process_text_mailing, state=MailingState.waiting_text_mailing)

    dp.register_message_handler(get_file, Text(equals='getfile', ignore_case=True))
    # dp.register_message_handler(get_file_cancel_handler, Text(equals='cancel', ignore_case=True), state='*')
    dp.register_message_handler(process_get_file, state=GetFile.FileName)
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
