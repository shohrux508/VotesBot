from sqlalchemy import delete
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.data.database import async_session
from app.data.models import Channel
# ChannelRepository предполагается содержит методы create() и list_all()
from app.data.repository import ChannelRepository

channels_rt = Router(name='channels')


@channels_rt.message(Command('channel_set'))
async def set_channel(msg: Message):
    """
    Ожидает текст вида:
    /channel_set <chat_id> <title>
    Например: /channel_set -1001234567890 my_channel_title

    При этом из таблицы channels удаляются все старые записи,
    и создаётся новая с переданными chat_id и title.
    """
    parts = msg.text.split(maxsplit=2)
    if len(parts) < 3:
        await msg.answer('Noto\'ri format. Quyidagi formatdan foydalaning:\n'
                         '/channel_set <kanal IDsi> <kanal linki>')
        return

    _, chat_id_str, url = parts
    try:
        chat_id = int(chat_id_str)
    except ValueError:
        await msg.answer('Kanal  <IDsi> hato.')
        return

    async with async_session() as session:
        # 1) удалить все старые записи
        await session.execute(delete(Channel))
        await session.commit()

        # 2) вставить новую запись
        new_channel = Channel(chat_id=chat_id, title=url)
        session.add(new_channel)
        await session.commit()

    await msg.answer(f'Kanal kiritildi:\n'
                     f'• chat_id: {chat_id}\n'
                     f'• link: {url}\n\n')


@channels_rt.message(Command('channel_get'))
async def get_channel(msg: Message):
    """
    Выдаёт информацию об одном сохранённом канале (если есть).
    """
    async with async_session() as session:
        channels = await ChannelRepository(Channel, session).list_all()
        if not channels:
            await msg.answer('Kanal kiritilmagan.')
            return

        # поскольку в таблице гарантированно одна запись, берём первую
        channel = channels[0]
        await msg.answer(f'Hozirgi kanal:\n'
                         f'• ID: {channel.id}\n'
                         f'• LINK: {channel.title}\n'
                         f'• CHAT_ID: {channel.chat_id}')
