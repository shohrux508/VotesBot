from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy.orm import selectinload

from app.data.database import async_session
from app.data.models import Category
from app.keyboards import categories_kb
from app.middleware.check_admin import AdminOnlyMiddleware
from app.utils import filter_data

admin_rt = Router(name='admins')
admin_rt.message.middleware(AdminOnlyMiddleware())


@admin_rt.message(Command('category'))
async def categories_list(msg: Message):
    await msg.answer(text='Toifalar',
                     reply_markup=await categories_kb(role='admin'))


def manage_category_kb(cat_id: int, run_vote_btn: bool = False, check_btn: bool = False) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            text="Nomzod qo'shish",
            callback_data=f"new-vote,add-candidate,category:{cat_id}"
        )
    ]

    if check_btn:
        buttons.append(
            InlineKeyboardButton(
                text="Tekshirish",
                callback_data=f"check,category_id:{cat_id}"
            )
        )
    if run_vote_btn:
        buttons.append(
            InlineKeyboardButton(
                text="Ovoz berishni to\'xtatish",
                callback_data=f"stop,category:{cat_id}"
            )
        )

    # Размещаем каждую кнопку в отдельном ряду
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[btn] for btn in buttons])
    return keyboard


@admin_rt.callback_query(F.data.startswith('check,category_id:'))
async def check_category(call: CallbackQuery):
    """
    Обработчик нажатия кнопки "Tekshirish".
    """
    category_id = filter_data(call.data, 'check,category_id:')
    async with async_session() as session:
        category = await session.get(
            Category,
            category_id,
            options=[selectinload(Category.candidates)]
        )
        # Здесь можно добавить логику по отображению списка кандидатов,
        # их голосов и т.д. В примере просто отправим сообщение:
        text = f"Toifa: {category.title}\nNomzodlar: ({len(category.candidates)}):\n"
        for cand in category.candidates:
            text += f"• {cand.name} — {cand.votes} ovoz\n"
        await call.answer(text, show_alert=True)
