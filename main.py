from aiogram import Dispatcher, Bot
from src.handlers import general
from src.handlers import track
from src.middlewares.db_middleware import DBMiddleware
import asyncio
import os


async def main():
    bot = Bot(os.getenv("TOKEN"))
    dp = Dispatcher()
    db_middleware = DBMiddleware()

    dp.message.middleware(db_middleware)
    dp.include_routers(
        general.router,
        track.router,
    )
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
