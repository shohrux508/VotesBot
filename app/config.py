import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pyee.asyncio import AsyncIOEventEmitter

load_dotenv('.env')
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
DATABASE_URL = os.getenv('DATABASE_URL')
event_bus = AsyncIOEventEmitter()
default = DefaultBotProperties(parse_mode='MARKDOWN')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Настройка логирования

class LoggingSettings(BaseSettings):
    telegram_enabled: bool = True
    telegram_log_bot_token: str = ""
    telegram_chat_id: str = ""
    level: str = "INFO"
    log_to_console: bool = True
    log_to_file: bool = False
    log_file_path: str = "logs/app.log"
    max_bytes: int = 5 * 1024 * 1024
    backup_count: int = 3
    formatter: str = "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
    telegram_formatter: str = "[%(levelname)s] %(name)s:%(lineno)d\n%(message)s"
    model_config = SettingsConfigDict(
        env_file=".env",  # путь до вашего .env
        env_file_encoding="utf-8",  # кодировка .env
        extra='ignore'
    )
