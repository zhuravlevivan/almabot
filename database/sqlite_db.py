import sqlite3 as sq
import os

from aiogram import types

from config import bot
from handlers.admin import is_admin

base = None
cur = None


def sql_start():
    global base, cur
    base = sq.connect('users.db', check_same_thread=False)
    cur = base.cursor()
    if base:
        print('Database Connect OK!')
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
                   chatid varchar(255),
                   login varchar(255),
                   name varchar(255),
                   lname varchar(255)
                )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS lections(
                    lectionid INTEGER,
                    path TEXT,
                    caption TEXT,
                    PRIMARY KEY("lectionid")
                )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS access(
                    auserid INTEGER,
                    alectionid  INTEGER
                )""")
    base.commit()


async def sql_add_user_cmd(message):
    global base, cur
    base = sq.connect('users.db', check_same_thread=False)
    cur = base.cursor()
    cur.execute(f"INSERT INTO users VALUES(?,?,?,?)", (message.chat.id,
                                                       message.from_user.username,
                                                       message.from_user.first_name,
                                                       message.from_user.last_name
                                                       ))
    base.commit()


async def show_users(message):
    global base, cur
    base = sq.connect('users.db', check_same_thread=False)
    cur = base.cursor()
    if is_admin(message):
        for value in cur.execute("SELECT * FROM users").fetchall():
            await bot.send_message(message.chat.id,
                                   f"<code>{value[0]}</code> @{value[1]} {value[2]} {value[3]}", parse_mode="html")


async def show_user_access(message):
    global base, cur
    base = sq.connect('users.db', check_same_thread=False)
    cur = base.cursor()
    user_access_list = []
    for value in cur.execute(f"SELECT * FROM access WHERE auserid = '{message}' ORDER BY auserid").fetchall():
        user_access_list.append(f"{value[1]}")

    return user_access_list


async def users_list(message):
    global base, cur
    base = sq.connect('users.db', check_same_thread=False)
    cur = base.cursor()
    users = []
    # if is_admin(message):
    for user in cur.execute("SELECT chatid FROM users").fetchall():
        users.append(*user)
    return users


async def show_files(message: types.Message):
    global base, cur
    base = sq.connect('users.db', check_same_thread=False)
    cur = base.cursor()
    files = os.listdir('files/')
    try:
        if is_admin(message) and len(files) > 0:
            for value in cur.execute("SELECT * FROM lections").fetchall():
                if len(cur.execute("SELECT * FROM lections").fetchall()) > 0:
                    await message.answer(
                        f"NAME=<code>{value[1]}</code>\nCAPTION={value[2]}", parse_mode="html")
                else:
                    await message.answer("Файлов нет")
        else:
            if len(files) > 0:
                await message.answer('Список файлов')
                for value in cur.execute("SELECT * FROM lections").fetchall():
                    if len(cur.execute("SELECT * FROM lections").fetchall()) > 0:
                        await message.answer(
                            f"NAME=<code>{value[1]}</code>\n{value[2]}", parse_mode="html")
            else:
                await message.answer('Файлов нет')
    except Exception as e:
        await message.answer("e")


async def get_caption(file_name):
    global base, cur
    base = sq.connect('users.db', check_same_thread=False)
    cur = base.cursor()
    return cur.execute(f"SELECT caption FROM lections WHERE path = '{file_name}'").fetchone()
