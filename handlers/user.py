import os
import config

from aiogram import types, Dispatcher
from create_bot import bot
from database import sqlite_db
from keyboards.user_kb import user_kb
from keyboards.admin_kb import admin_menu_kb


async def start_cmd(message: types.Message):
    sqlite_db.cur.execute(
        f"SELECT chatid FROM users WHERE chatid = '{message.chat.id}'")  # есть ли такая запись в таблице
    if sqlite_db.cur.fetchone() is None:  # если такой записи нет, то:
        sqlite_db.cur.execute(f"INSERT INTO users VALUES(?,?,?,?)", (message.chat.id,
                                                                     message.from_user.username,
                                                                     message.from_user.first_name,
                                                                     message.from_user.last_name
                                                                     ))
        sqlite_db.base.commit()
        await bot.send_message(message.chat.id, "Привет! \nСписок доступных команд /help.")
        if message.chat.id not in config.ADMINS:
            for ids in config.ADMINS:
                # print(i)
                await bot.send_message(ids,
                                       f"Сообщение от пользователя: \n"
                                       f"Логин: @{message.from_user.username} \n"
                                       f"Имя: {message.from_user.first_name} \n"
                                       f"Фамилия: {message.from_user.last_name} \n"
                                       f"id: `{message.chat.id}`", parse_mode="MarkdownV2"
                                       )
                ids += 1
    else:
        await bot.send_message(message.chat.id, "Привет! \nСписок доступных команд /help.")



async def help_cmd(message: types.Message):
    if message.chat.id not in config.ADMINS:
        await bot.send_message(message.chat.id,
                               "Список доступных лекций: /files\n"
                               "Чтобы получить файл: /getfile", reply_markup=user_kb
                               )
    else:
        await bot.send_message(message.chat.id,
                               "Действия кнопок\n"
                               "Вход в админку __admin__\n"
                               "Список загруженных файлов __files__\n"
                               "Удалить файл по имени __remove__\n"
                               "Переименовать файл __rename__\n"
                               "Список пользователей __users__\n",
                               parse_mode="MarkdownV2",
                               reply_markup=admin_menu_kb
                               )


async def files_cmd(message):
    files = os.listdir('files/')
    if len(files) > 0:
        await bot.send_message(message.chat.id, 'Список файлов')
        for file in files:
            await bot.send_message(message.chat.id, f"`{file}`", parse_mode="MarkdownV2")
    else:
        await bot.send_message(message.chat.id, 'Файлов нет')


def register_handlers_user(dp: Dispatcher):
    dp.register_message_handler(start_cmd, commands=['start'])
    dp.register_message_handler(help_cmd, commands=['help'])
    dp.register_message_handler(files_cmd, commands=['files'])
