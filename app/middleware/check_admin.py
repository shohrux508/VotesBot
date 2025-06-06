from typing import Dict, Any, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

from app.config import ADMIN_IDS


class AdminOnlyMiddleware(BaseMiddleware):
    """
    Middleware - для проверки входящих сообщений,
    для подтверждения дальнейших обработок,
    в зависимости от выполненных условий(состоит в списке администраторов)
    """

    async def __call__(self, handler: Callable, event: Message, data: Dict[str, Any]):
        if str(event.from_user.id) in list(ADMIN_IDS.split(',')):
            return await handler(event, data)
        await event.answer('Эта команда доступна только администраторам!')
