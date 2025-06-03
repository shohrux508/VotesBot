import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from app.config import BOT_TOKEN, LoggingSettings
import pytz
from datetime import datetime

from app.logger_module.config import LoggingConfig
from app.users import user_rt
from app.admins import admin_rt
import logging

default = DefaultBotProperties(parse_mode='MARKDOWN')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
settings = LoggingSettings()  # прочитает .env автоматически
LoggingConfig(settings).setup()


def get_logger(name: str = __name__) -> logging.Logger:
    return logging.getLogger(name)


def setup_routers():
    dp.include_router(user_rt)
    dp.include_router(admin_rt)


def setup_timezone():
    pytz.timezone("Asia/Tashkent")
    datetime.now().replace(tzinfo=pytz.utc)


async def main():
    setup_timezone()
    setup_routers()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
