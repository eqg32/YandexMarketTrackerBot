from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types


def main_kb() -> types.ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for text in ["/track", "/untrack", "/list", "/help"]:
        kb.button(text=text)
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
