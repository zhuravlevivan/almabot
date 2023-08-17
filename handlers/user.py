from aiogram import types, Dispatcher
from create_bot import dp, bot
import config
import sqlite3
from keyboards import user_kb


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


# @dp.message_handler(commands=['start'])
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
        await bot.send_message(message.chat.id, "Привет! \nСписок доступных команд /help.", reply_markup=user_kb)
    else:
        await bot.send_message(message.chat.id, "Привет! \nСписок доступных команд /help.", reply_markup=user_kb)
        if message.chat.id in config.ADMINS:
            for _ in config.ADMINS:
                await bot.send_message(_,
                                       f"Сообщение от пользователя: \n"
                                       f"Логин: @{message.from_user.username} \n"
                                       f"Имя: {message.from_user.first_name} \n"
                                       f"Фамилия: {message.from_user.last_name} \n"
                                       f"id: `{message.chat.id}`", parse_mode="MarkdownV2"
                                       )
                _ += 1


# @dp.message_handler(commands=['help'])
async def help_cmd(message):
    if message.chat.id not in config.ADMINS:
        await bot.send_message(message.chat.id,
                               "Список доступных лекций: /files\n"
                               "Чтобы получить файл: /getfile"
                               )
    else:
        await bot.send_message(message.chat.id,
                               "Вход в админку /admin\n"
                               "Список загруженных файлов /files\n"
                               "Удалить файл по имени /rmfile\n"
                               "Переименовать файл /rename\n"
                               "Список пользователей /users\n"
                               )


def register_handlers_user(dp: Dispatcher):
    dp.register_message_handler(start_cmd, commands=['start'])
    dp.register_message_handler(help_cmd, commands=['help'])

