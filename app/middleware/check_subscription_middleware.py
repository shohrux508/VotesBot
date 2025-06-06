from aiogram import BaseMiddleware

from app.data.database import async_session
from app.data.models import Channel
from app.data.repository import ChannelRepository
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        # Проверяем только личные чаты (bot <-> user)
        if event.chat.type == 'private':
            user_id = event.from_user.id

            # 1) получаем chat_id канала из БД (если он задан)
            async with async_session() as session:
                channels = await ChannelRepository(Channel, session).list_all()

            if channels:
                channel_chat_id = channels[0].chat_id

                try:
                    # 2) запрашиваем статус пользователя в этом канале
                    member = await data['bot'].get_chat_member(
                        chat_id=channel_chat_id,
                        user_id=user_id
                    )
                except Exception:
                    # если канал неправильно задан или бот не админ — просто пропускаем,
                    # чтобы основной код мог выдать ошибку или напомнить настроить канал
                    return await handler(event, data)
                invite = await event.bot.create_chat_invite_link(chat_id=channel_chat_id)
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text=channels[0].title, url=str(invite))]])
                # 3) если статус – left или kicked, просим подписаться
                if member.status in ('left', 'kicked'):
                    await event.answer(
                        '⚠️ Botdan foydalanish uchun kanalga obuna bo\'lishingiz kerak.\n'
                        'Obuna bo\'lib boshqatdan urining!.', reply_markup=keyboard
                    )
                    return  # НЕ вызываем handler, прекращаем цепочку

        # Если всё ок — передаём в следующий обработчик
        return await handler(event, data)
