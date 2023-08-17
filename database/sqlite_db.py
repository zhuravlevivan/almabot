import sqlite3 as sq


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
