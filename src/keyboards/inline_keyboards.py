from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def cart_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="previous", callback_data="cart_previous")
    )
    builder.add(InlineKeyboardButton(text="next", callback_data="cart_next"))
    builder.add(InlineKeyboardButton(text="back", callback_data="main_menu"))
    builder.adjust(2)
    return builder.as_markup()


def main_menu_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Track", callback_data="main_menu_track")
    )
    builder.add(
        InlineKeyboardButton(text="Untrack", callback_data="main_menu_untrack")
    )
    builder.add(
        InlineKeyboardButton(text="List", callback_data="main_menu_list")
    )
    builder.adjust(2)
    return builder.as_markup()
