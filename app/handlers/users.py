from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy.exc import IntegrityError

from app.config import ADMIN_IDS
from app.data.database import async_session
from app.data.models import Candidate, Vote
from app.keyboards import main_kb, candidates_kb
from app.utils import filter_data
from sqlalchemy import update, insert

user_rt = Router(name='users')


# /start - для администраторов и для пользователей.
@user_rt.message(Command('start'))
async def answer(msg: Message):
    user_id = msg.from_user.id

    if str(user_id) in list(ADMIN_IDS):
        await msg.answer('/new_category - boshlash'
                         '/category - boshqarish'
                         '/channel_set - kanalni ozgartirish'
                         '/channel_get - hozirgi kanal')
        return
    await msg.answer('Assolomu alaykum', reply_markup=main_kb())


# /deep-link - для голосования
@user_rt.message(CommandStart(deep_link=True))
async def handle_vote_start(msg: Message, command: CommandObject):
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

        await msg.answer("✅ Ovozingiz muvaffaqiyatli qabul qilindi!")
    except IntegrityError:
        # IntegrityError возникает, если уже есть запись user_id+candidate_id
        await msg.answer("Siz allaqachon ovoz bergansiz!")
    except Exception:
        await msg.answer("Xatolik yuz berdi, iltimos qayta urinib ko‘ring.")


# vote via buttons
@user_rt.callback_query(F.data.startswith('categories:'))
async def candidates_list(call: CallbackQuery):
    category_id = filter_data(call.data, 'categories:')

    await call.bot.edit_message_text(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        text='Nomzodlar: ',
        reply_markup=await candidates_kb(category_id=int(category_id))
    )


@user_rt.callback_query(F.data.startswith('candidates:'))
async def vote(call: CallbackQuery):
    candidate_id = filter_data(call.data, 'candidates:')
    user_id = call.from_user.id

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

        await call.message.answer("✅ Ovozingiz muvaffaqiyatli qabul qilindi!")
    except IntegrityError:
        # IntegrityError возникает, если уже есть запись user_id+candidate_id
        await call.message.answer("Siz allaqachon ovoz bergansiz!")
    except Exception:
        await call.message.answer(
            "Xatolik yuz berdi, iltimos qayta urinib ko‘ring."
        )

    await call.bot.edit_message_text(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        text='✅ Ovozingiz muvaffaqiyatli qabul qilindi!'
    )
