import sqlite3 as sq
import gspread

from aiogram import types

from config import bot, google_json, tab_name
from handlers.admin import is_admin, datetime

base = None
cur = None

gc = gspread.service_account(filename=google_json)
sh = gc.open(tab_name)
worksheet = sh.get_worksheet(0)
worksheet2 = sh.get_worksheet(1)


def sql_start():
    global base, cur
    base = sq.connect('database/users.db', check_same_thread=False)
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
    base = sq.connect('database/users.db', check_same_thread=False)
    cur = base.cursor()
    cur.execute(f"INSERT INTO users VALUES(?,?,?,?)", (message.chat.id,
                                                       message.from_user.username,
                                                       message.from_user.first_name,
                                                       message.from_user.last_name
                                                       ))
    base.commit()
    await add_users_to_sheets(message.chat.id,
                              message.from_user.username,
                              message.from_user.first_name,
                              message.from_user.last_name)


async def show_users(message):
    global base, cur
    base = sq.connect('database/users.db', check_same_thread=False)
    cur = base.cursor()
    if is_admin(message):
        for value in cur.execute("SELECT * FROM users").fetchall():
            await bot.send_message(message.chat.id,
                                   f"<code>{value[0]}</code> @{value[1]} {value[2]} {value[3]}", parse_mode="html")


async def show_user_access(message):
    global base, cur
    base = sq.connect('database/users.db', check_same_thread=False)
    cur = base.cursor()
    user_access_list = []
    for value in cur.execute(f"SELECT * FROM access WHERE auserid = '{message}' ORDER BY auserid").fetchall():
        user_access_list.append(f"{value[1]}")

    return user_access_list


async def users_list(message):
    global base, cur
    base = sq.connect('database/users.db', check_same_thread=False)
    cur = base.cursor()
    users = []
    # if is_admin(message):
    for user in cur.execute("SELECT chatid FROM users").fetchall():
        users.append(*user)
    return users


async def show_files(message: types.Message):
    global base, cur
    base = sq.connect('database/users.db', check_same_thread=False)
    cur = base.cursor()
    # files = os.listdir('files/')
    try:
        if is_admin(message):
            if len(cur.execute("SELECT * FROM lections").fetchall()) != 0:
                for value in cur.execute("SELECT * FROM lections").fetchall():
                    await message.answer(
                        f"NAME=<code>{value[1]}</code>\nCAPTION={value[2]}", parse_mode="html")
            else:
                await message.answer("Файлов нет")
        else:
            if len(cur.execute("SELECT * FROM lections").fetchall()) != 0:
                await message.answer('Список файлов')
                for value in cur.execute("SELECT * FROM lections").fetchall():
                    await message.answer(
                            f"NAME=<code>{value[1]}</code>\n{value[2]}", parse_mode="html")
            else:
                await message.answer('Файлов нет')

    except OSError as e:
        await message.answer(str(e))


async def get_caption(file_name):
    global base, cur
    base = sq.connect('database/users.db', check_same_thread=False)
    cur = base.cursor()
    return cur.execute(f"SELECT caption FROM lections WHERE path = '{file_name}'").fetchone()


async def add_access_to_sheets(user_id, lecture_name):
    date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    data = [user_id, lecture_name, date]
    worksheet.append_row(data)


async def add_users_to_sheets(user_id, u_name, f_name, l_name):
    date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    data = [user_id, u_name, f_name, l_name, date]
    worksheet2.append_row(data)


async def del_access_from_sheet(user_id, lecture_name):
    cell_list = worksheet.findall(str(user_id))
    cell2 = reversed(cell_list)  # Разворачиваем, чтобы удалять с конца
    data = [str(user_id), lecture_name]
    for r in cell2:
        if data[0] == worksheet.row_values(r.row)[0] and data[1] == worksheet.row_values(r.row)[1]:
            worksheet.delete_row(r.row)


async def del_item_from_sheet(item):
    cell_list = worksheet.findall(str(item))
    cell_list2 = worksheet2.findall(str(item))
    cell_rev = reversed(cell_list)
    cell_rev2 = reversed(cell_list2)
    for r in cell_rev:
        worksheet.delete_rows(r.row)
    for r in cell_rev2:
        worksheet2.delete_rows(r.row)


async def rename_file_in_sheet(old_name, new_name):
    cell_list = worksheet.findall(old_name)
    cell2 = reversed(cell_list)
    for r in cell2:
        worksheet.update_cell(r.row, r.col, new_name)
