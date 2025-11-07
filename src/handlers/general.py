from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from src.keyboards.inline_keyboards import main_menu_inline_kb
import sqlite3

router = Router()


@router.message(StateFilter(None), Command("start"))
async def start(
    message: types.Message, state: FSMContext, con: sqlite3.Connection
):
    await message.answer(
        "This is Yandex Market tracker bot. Below is the main menu."
    )
    await main_menu(update=message, state=state, con=con)


@router.message(StateFilter(None), Command("main-menu"))
async def main_menu(
    update: types.Message | types.CallbackQuery,
    state: FSMContext,
    con: sqlite3.Connection,
):
    await state.clear()
    cur = con.cursor()
    goods_tracked = cur.execute(
        """SELECT count (*) FROM user_goods WHERE user_id = ?""",
        (update.from_user.id,),
    ).fetchone()[0]
    match type(update):
        case types.CallbackQuery:
            await update.message.answer(
                f"Currently tracking *{goods_tracked}* goods\nActions:",
                reply_markup=main_menu_inline_kb(),
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        case types.Message:
            await update.answer(
                f"Currently tracking *{goods_tracked}* goods\nActions:",
                reply_markup=main_menu_inline_kb(),
                parse_mode=ParseMode.MARKDOWN_V2,
            )
    cur.close()


@router.message(Command("cancel"))
async def cancel(
    message: types.Message, state: FSMContext, con: sqlite3.Connection
):
    await state.clear()
    await message.answer("Success!")
    await main_menu(update=message, state=state, con=con)
