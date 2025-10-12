from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.enums.parse_mode import ParseMode
from aiogram.utils.formatting import Text
from aiogram.fsm.context import FSMContext
from urllib.error import HTTPError
from src.keyboards.keyboard import main_kb
from src.good import Good
import sqlite3


router = Router()
HELP_MESSAGE = """This is a Yandex Market tracker bot. Here are the available commands:
/start, /help - display this message.
/track - track a good.
/untrack - untrack a good.
/list - list all the tracked goods with their titles, prices and descriptions."""


@router.message(StateFilter(None), Command(commands=["start", "help"]))
async def help(message: types.Message):
    await message.answer(HELP_MESSAGE, reply_markup=main_kb())


@router.message(StateFilter(None), Command("list"))
async def list_goods(message: types.Message, con: sqlite3.Connection):
    id = message.from_user.id
    cur = con.cursor()
    goods_tuple = cur.execute(
        """SELECT goods.part_number, goods.title, goods.price, goods.description
        FROM goods JOIN user_goods ON goods.part_number = user_goods.part_number
        WHERE user_id = ?""",
        (id,),
    ).fetchall()
    goods = [Good.from_tuple(*good) for good in goods_tuple]
    if goods:
        await message.answer("Here are the goods you track:")
        for good in goods:
            try:
                await good()
            except HTTPError:
                await message.answer(
                    "Could not connect to Yandex Market!",
                    reply_markup=main_kb(),
                )
            except IndexError:
                await message.answer(
                    f"Could not find a good with part number {good.part_number}! It might have been removed from Yandex Market.",
                    reply_markup=main_kb(),
                )
                cur.execute(
                    "DELETE FROM goods WHERE part_number = ?",
                    (good.part_number,),
                )
            else:
                cur.execute(
                    """UPDATE goods SET title = ?, price = ?, description = ?
                    WHERE part_number = ?""",
                    (
                        good.title,
                        good.price,
                        good.description,
                        good.part_number,
                    ),
                )
                await message.answer(
                    good.to_message().as_markdown(),
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
    else:
        await message.answer(
            "You currently do not track any goods!", reply_markup=main_kb()
        )
    con.commit()
    cur.close()


@router.message(Command("cancel"))
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Success!", reply_markup=main_kb())
    await state.clear()
