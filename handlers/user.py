import os

from aiogram import types, Dispatcher
from create_bot import bot
import config
import sqlite3
from keyboards.user_kb import user_kb
from keyboards.admin_kb import admin_menu_kb


conn = sqlite3.connect('users.db', check_same_thread=False)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users(
               chatid varchar(255),
               login varchar(255),
               name varchar(255),
               lname varchar(255)
            )""")
cur.execute("""CREATE TABLE IF NOT EXISTS lections(
                lectionid INTEGER,
                path TEXT,
                PRIMARY KEY("lectionid")
            )""")
cur.execute("""CREATE TABLE IF NOT EXISTS access(
                auserid INTEGER,
                alectionid  INTEGER
            )""")
conn.commit()


async def start_cmd(message: types.Message):
    cur.execute(
        f"SELECT chatid FROM users WHERE chatid = '{message.chat.id}'")  # есть ли такая запись в таблице
    if cur.fetchone() is None:  # если такой записи нет, то:
        cur.execute(f"INSERT INTO users VALUES(?,?,?,?)", (message.chat.id,
                                                           message.from_user.username,
                                                           message.from_user.first_name,
                                                           message.from_user.last_name
                                                           ))
        conn.commit()
        await bot.send_message(message.chat.id, "Привет! \nСписок доступных команд /help.")
    else:
        await bot.send_message(message.chat.id, "Привет! \nСписок доступных команд /help.")
        if message.chat.id not in config.ADMINS:
            for i in os.getenv('ADMINS'):
                await bot.send_message(i,
                                       f"Сообщение от пользователя: \n"
                                       f"Логин: @{message.from_user.username} \n"
                                       f"Имя: {message.from_user.first_name} \n"
                                       f"Фамилия: {message.from_user.last_name} \n"
                                       f"id: `{message.chat.id}`", parse_mode="MarkdownV2"
                                       )
                i += 1


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


def register_handlers_user(dp: Dispatcher):
    dp.register_message_handler(start_cmd, commands=['start'])
    dp.register_message_handler(help_cmd, commands=['help'])

