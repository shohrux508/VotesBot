from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy import update
from sqlalchemy.orm import selectinload

from app.config import bot
from app.data.database import async_session
from app.data.models import Category
from app.utils import filter_data

admin_publish_rt = Router(name='admin_pub')


class PublishStates(StatesGroup):
    get_channel = State()


@admin_publish_rt.callback_query(F.data.startswith('new-vote,run,category:'))
async def run(call: CallbackQuery, state: FSMContext):
    cat_id = filter_data(call.data, 'new-vote,run,category:')
    await state.update_data(cat_id=cat_id)
    await call.message.answer('Kanal IDsini kiriting: \n'
                              'Bekor qilish: /break')
    await state.set_state(PublishStates.get_channel)


@admin_publish_rt.message(StateFilter(PublishStates.get_channel))
async def answer(msg: Message, state: FSMContext):
    if 'break' in msg.text:
        await state.clear()
        await msg.answer('Bekor qilindi!')
        return
    channel_id = msg.text
    cat_id = (await state.get_data()).get('cat_id')
    await state.clear()
    btn_list = []

    async with async_session() as session:
        category = await session.get(Category, cat_id, options=[selectinload(Category.candidates)])
        ss = []
        for candidate in category.candidates:
            text = f'{candidate.name}\n'
            btn = InlineKeyboardButton(text=f"{candidate.name} - {candidate.votes}",
                                       url=f"https://t.me/shohruxs_bot?start=vote_{candidate.id}")
            btn_list.append(btn)
            ss.append(text)
        update_stmt = (update(Category).where(Category.id == cat_id).values(is_active=1))
        await session.execute(update_stmt)
        await session.commit()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[i] for i in btn_list])
    await msg.answer(category.title, reply_markup=keyboard)
    try:
        await bot.send_message(chat_id=channel_id, text=category.title, reply_markup=keyboard)
    except:
        await msg.answer('Kanalga joylashda hatolik yuz berdi. \n'
                         'Kanal IDsini tekshiring!\n'
                         '⚠️ Eslatma! Bot Kanalda admin bolishi zarur.')


