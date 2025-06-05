from aiogram import Router, F
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, CallbackQuery
from pydantic import BaseModel
from sqlalchemy import update, insert
from sqlalchemy.exc import IntegrityError

from app.config import bot
from app.data.database import async_session
from app.data.models import Candidate, Vote
from app.utils import filter_data

user_rt = Router(name='users')


def start_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Kanalga obuna bo'lish", url='https://t.me/shohrux_yigitaliev')]
    ])


@user_rt.message(CommandStart(deep_link=True))
async def handle_vote_start(msg: Message, command: CommandObject):
    user_id = msg.from_user.id

    # 1) Сначала проверяем, подписан ли юзер на канал
    try:
        member = await bot.get_chat_member(-1002592117570, user_id)
    except Exception:
        member = None

    if not member or member.status in (
            ChatMemberStatus.LEFT,
            ChatMemberStatus.KICKED
    ):
        # Формируем кнопку для подписки
        subscribe_btn = InlineKeyboardButton(
            text="Obuna bo'lish",
            url=f"https://t.me/shohrux_yigitaliev"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[[subscribe_btn]])

        await msg.answer(
            "Iltimos, ovoz berishdan avval kanalga obuna bo‘ling:",
            reply_markup=kb
        )
        return

    if not (command.args and command.args.startswith("vote_")):
        await msg.answer("Bu bot orqali siz ovoz berishingiz mumkin.")
        return

    candidate_id = int(command.args.split("_")[1])
    user_id = msg.from_user.id

    try:
        async with async_session() as session:
            # 1) Сначала пытаемся добавить запись в таблицу Vote.
            stmt_insert = insert(Vote).values(
                user_id=user_id,
                candidate_id=candidate_id
            )
            await session.execute(stmt_insert)
            stmt_update = (
                update(Candidate)
                .where(Candidate.id == candidate_id)
                .values(votes=Candidate.votes + 1)
            )
            await session.execute(stmt_update)

            await session.commit()

        await msg.answer("Ovozingiz qabul qilindi!")
    except IntegrityError:
        # IntegrityError возникает, если уже есть запись user_id+candidate_id
        await msg.answer("Siz allaqachon ovoz bergansiz!")
    except Exception:
        await msg.answer("Xatolik yuz berdi, iltimos qayta urinib ko‘ring.")
