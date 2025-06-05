from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.orm import selectinload

from app.config import bot
from app.data.database import async_session
from app.data.models import Category
from app.utils import filter_data

admin_publish_rt = Router(name='admin_pub')


@admin_publish_rt.callback_query(F.data.startswith('new-vote,run,category:'))
async def run(call: CallbackQuery):
    cat_id = filter_data(call.data, 'new-vote,run,category:')
    btn_list = []

    async with async_session() as session:
        category = await session.get(Category, cat_id, options=[selectinload(Category.candidates)])
        ss = []
        for candidate in category.candidates:
            text = f'{candidate.name}\n'
            btn = InlineKeyboardButton(text=f"{candidate.name} - {candidate.votes}", url=f"https://t.me/shohruxs_bot?start=vote_{candidate.id}")
            btn_list.append(btn)
            ss.append(text)
        ss = '\n'.join(ss)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[i] for i in btn_list])
    await bot.send_message(chat_id=-1002592117570, text=category.title, reply_markup=keyboard)
    await call.message.answer(category.title, reply_markup=keyboard)

