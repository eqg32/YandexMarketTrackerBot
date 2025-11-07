from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from src.handlers.general import main_menu
from src.states.track import TrackState, UntrackState
from src.utils.good import Good
from urllib.error import HTTPError
from contextlib import suppress
import sqlite3


router = Router()


@router.callback_query(StateFilter(None), F.data == "main_menu_track")
async def track(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Fine! Send me the part number of your good!"
    )
    await state.set_state(TrackState.entering_part_number)
    await callback.answer()


@router.message(TrackState.entering_part_number)
async def add_good(
    message: types.Message, con: sqlite3.Connection, state: FSMContext
):
    try:
        good = Good(int(message.text))
        await good()
    except ValueError:
        await message.answer("The part number should be a number!")
    except HTTPError:
        await message.answer(
            "Could not connect to Yandex Market!", reply_markup=start_kb()
        )
        await state.clear()
    except IndexError:
        await message.answer(
            "Unfortunately, we could not parse a good! This might have happened because of changes from Yandex Market",
            reply_markup=start_kb(),
        )
        await state.clear()
    else:
        cur = con.cursor()
        with suppress(sqlite3.IntegrityError):
            cur.execute("INSERT INTO goods VALUES (?, ?, ?, ?)", tuple(good))
        with suppress(sqlite3.IntegrityError):
            cur.execute(
                "INSERT INTO user_goods VALUES (?, ?)",
                (message.from_user.id, message.text),
            )
        cur.close()
        con.commit()
        await message.answer("Success!")
        await main_menu(message, state, con)
    await state.clear()


@router.callback_query(StateFilter(None), F.data == "main_menu_untrack")
async def untrack(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Fine! Send me the part number of your good!"
    )
    await state.set_state(UntrackState.entering_part_number)
    await callback.answer()


@router.message(UntrackState.entering_part_number)
async def remove_good(
    message: types.Message, con: sqlite3.Connection, state: FSMContext
):
    if not message.text.isdecimal():
        await message.answer("This is not a part number!")
        return
    cur = con.cursor()
    cur.execute(
        "DELETE FROM user_goods WHERE user_id = ? AND part_number = ?",
        (message.from_user.id, message.text),
    )
    tracked_by = cur.execute(
        "SELECT user_id FROM user_goods WHERE part_number = ?", (message.text,)
    ).fetchall()
    if not tracked_by:
        cur.execute("DELETE FROM goods WHERE part_number = ?", (message.text,))
    cur.close()
    con.commit()
    await message.answer("Success!")
    await main_menu(message, state, con)
    await state.clear()
