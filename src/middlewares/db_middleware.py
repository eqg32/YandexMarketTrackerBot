from aiogram import BaseMiddleware
import sqlite3


class DBMiddleware(BaseMiddleware):
    def __init__(self, file_name: str = "db.sqlite3"):
        self.file_name = file_name
        self.con = sqlite3.connect(self.file_name)
        cur = self.con.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS goods (
            part_number INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            price INTEGER NOT NULL,
            description TEXT
            )"""
        )

        cur.execute(
            """CREATE TABLE IF NOT EXISTS user_goods (
            user_id INTEGER NOT NULL,
            part_number INTEGER REFERENCES goods (part_number),
            PRIMARY KEY (user_id, part_number)
            )"""
        )

        cur.close()

    async def __call__(self, handler, event, data):
        data["con"] = self.con
        return await handler(event, data)
