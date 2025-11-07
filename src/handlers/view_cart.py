from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from src.handlers import general
from src.keyboards.inline_keyboards import cart_inline_kb
from src.utils.good import Good
from src.utils.cycled_list import CycledList
from src.states.view_cart import ViewCart
from urllib.error import HTTPError
from contextlib import suppress
import sqlite3

router = Router()


@router.callback_query(StateFilter(None), F.data == "main_menu_list")
async def view_cart(
    callback: CallbackQuery, con: sqlite3.Connection, state: FSMContext
):
    message = callback.message
    id = callback.from_user.id
    cur = con.cursor()
    goods_tuple = cur.execute(
        """SELECT DISTINCT goods.part_number, goods.title, goods.price, goods.description
        FROM goods JOIN user_goods ON goods.part_number = user_goods.part_number
        WHERE user_id = ?""",
        (id,),
    ).fetchall()
    goods = [Good.from_tuple(*good) for good in goods_tuple]
    if goods:
        for good in goods:
            try:
                await good()
            except HTTPError:
                await message.answer(
                    "Could not connect to Yandex Market!",
                )
                await general.main_menu(callback, state, con)
            except IndexError:
                await message.answer(
                    f"Could not find a good with part number {good.part_number}! It might have been removed from Yandex Market.",
                )
                cur.execute(
                    "DELETE FROM goods WHERE part_number = ?",
                    (good.part_number,),
                )
                await general.main_menu(callback, state, con)
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
            goods[0].to_message().as_markdown(),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=cart_inline_kb(),
        )
        await state.set_state(ViewCart.view_cart)
        await state.update_data(goods=CycledList(goods))
    else:
        await message.answer("You currently do not track any goods!")
    cur.close()
    callback.answer()


@router.callback_query(
    F.data.startswith("cart"), StateFilter(ViewCart.view_cart)
)
async def cart_previous_good(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    match callback.data.split("_")[1]:
        case "previous":
            good = user_data["goods"].previous()
        case "next":
            good = user_data["goods"].next()
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            good.to_message().as_markdown(),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=cart_inline_kb(),
        )
    await callback.answer()


@router.callback_query(F.data == "main_menu", StateFilter(ViewCart.view_cart))
async def main_menu(
    callback: CallbackQuery, state: FSMContext, con: sqlite3.Connection
):
    await state.clear()
    await general.main_menu(callback, state, con)
    await callback.answer()
