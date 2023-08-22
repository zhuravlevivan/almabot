import sqlite3 as sq
import config
import os
from create_bot import bot

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
                    PRIMARY KEY("lectionid")
                )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS access(
                    auserid INTEGER,
                    alectionid  INTEGER
                )""")
    base.commit()


async def sql_add_users_cmd(message):
    cur.execute(f"INSERT INTO users VALUES(?,?,?,?)", (message.chat.id,
                                                       message.from_user.username,
                                                       message.from_user.first_name,
                                                       message.from_user.last_name
                                                       ))


async def show_users(message):
    if message.chat.id in config.ADMINS:
        for value in cur.execute("SELECT * FROM users").fetchall():
            await bot.send_message(message.chat.id,
                                   f"{value[1]} <code>{value[0]}</code> {value[2]} {value[3]}", parse_mode="html")


async def show_files(message):
    if message.chat.id in config.ADMINS:
        for value in cur.execute("SELECT * FROM lections").fetchall():
            if len(cur.execute("SELECT * FROM lections").fetchall()) > 0:
                await bot.send_message(message.chat.id,
                                       f"ID=<code>{value[0]}</code> NAME=<code>{value[1]}</code>", parse_mode="html")
            else:
                await bot.send_message(message.chat.id, "Файлов нет")
    else:
        files = os.listdir('files/')
        if len(files) > 0:
            await bot.send_message(message.chat.id, 'Список файлов')
            for file in files:
                await bot.send_message(message.chat.id, f"`{file}`", parse_mode="MarkdownV2")
        else:
            await bot.send_message(message.chat.id, 'Файлов нет')
