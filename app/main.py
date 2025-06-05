import asyncio

from app.handlers.admin_create import admin_create_rt
from app.handlers.admin_publish import admin_publish_rt
from app.config import LoggingSettings, dp, bot
import pytz
from datetime import datetime

from app.data.database import init_db
from app.logger_module.config import LoggingConfig
from app.handlers.users import user_rt
from app.handlers.admin_read import admin_rt
import logging


settings = LoggingSettings()  # прочитает .env автоматически
LoggingConfig(settings).setup()


def get_logger(name: str = __name__) -> logging.Logger:
    return logging.getLogger(name)


def setup_routers():
    dp.include_router(user_rt)
    dp.include_router(admin_rt)
    dp.include_router(admin_create_rt)
    dp.include_router(admin_publish_rt)


def setup_timezone():
    pytz.timezone("Asia/Tashkent")
    datetime.now().replace(tzinfo=pytz.utc)


async def main():
    setup_timezone()
    setup_routers()
    await init_db()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
