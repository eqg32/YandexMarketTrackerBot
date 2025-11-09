from aiogram import Dispatcher, Bot
from src.handlers import general
from src.handlers import track
from src.handlers import view_cart
from src.middlewares.db_middleware import DBMiddleware
import tomllib
import asyncio
import os


async def main():
    token = os.getenv("TOKEN")
    if token is None:
        with open("config.toml", "rb") as file:
            config = tomllib.load(file)
            try:
                token = config["general"]["token"]
            except KeyError:
                print("No token specified!")
                return
    bot = Bot(token)
    dp = Dispatcher()
    db_middleware = DBMiddleware()

    dp.update.middleware(db_middleware)
    dp.include_routers(
        general.router,
        track.router,
        view_cart.router,
    )
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
