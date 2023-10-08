import config
from aiogram import types
from config import bot
from database import sqlite_db
from keyboards.user_kb import user_kb
from keyboards.admin_kb import admin_menu_kb
from handlers.admin import is_admin


async def start_cmd(message: types.Message):
    sqlite_db.cur.execute(
        f"SELECT chatid FROM users WHERE chatid = '{message.chat.id}'")  # есть ли такая запись в таблице

    if sqlite_db.cur.fetchone() is None:  # если такой записи нет, то:
        await sqlite_db.sql_add_user_cmd(message)
        await bot.send_message(message.chat.id, "Привет! \nСписок доступных команд /help.")
        if not is_admin(message):
            for ids in config.ADMINS:
                await bot.send_message(ids,
                                       f"Новый пользователь:\n"
                                       f"Логин: @{message.from_user.username} \n"
                                       f"Имя: {message.from_user.first_name} \n"
                                       f"Фамилия: {message.from_user.last_name} \n"
                                       f"id: `{message.chat.id}`", parse_mode="MarkdownV2"
                                       )
                ids += 1
    else:
        await bot.send_message(message.chat.id, "Привет! \nСписок доступных команд /help.")


async def help_cmd(message: types.Message):
    if not is_admin(message):
        await bot.send_message(message.chat.id,
                               "Список лекций: __files__\n"
                               "Чтобы получить файл: __getfile__\n"
                               "Узнать свой ID: __my id__\n",
                               parse_mode="MarkdownV2",
                               reply_markup=user_kb
                               )
    else:
        await bot.send_message(message.chat.id,
                               "Действия кнопок\n"
                               "Вход в админку __admin__\n"
                               "Список загруженных файлов __files__\n"
                               "Удалить файл по имени __remove__\n"
                               "Переименовать файл __rename__\n"
                               "Список пользователей __users__\n"
                               "Получить файл __getfile__\n"
                               "Добавить описание файла __caption__",
                               parse_mode="MarkdownV2",
                               reply_markup=admin_menu_kb
                               )


async def files_cmd(message):
    await sqlite_db.show_files(message)


async def my_id(message: types.Message):
    await message.answer(f'ID `{message.chat.id}`', parse_mode="MarkdownV2")
