from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select

from app.data.database import async_session
from app.data.models import Category, Candidate
from app.data.repository import CategoryRepository


def start_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Kanalga obuna bo'lish", url='https://t.me/shohrux_yigitaliev')]
    ])


def main_kb(role: str = 'user') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Toifalar', callback_data=f'{role},categories')],
    ])


async def categories_kb(role: str = 'user') -> InlineKeyboardMarkup:
    async with async_session() as session:
        repo = CategoryRepository(Category, session)
        categories = await repo.list_all()
        btn_list = []
        for category in categories:
            btn = InlineKeyboardButton(text=str(category.title), callback_data=f'{role},categories:{category.id}')
            btn_list.append(btn)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[btn] for btn in btn_list])
    return keyboard


async def candidates_kb(category_id: int, role: str = 'user') -> InlineKeyboardMarkup:
    async with async_session() as session:
        # Выполняем запрос: все кандидаты, у которых поле category_id равно переданному
        result = await session.execute(
            select(Candidate).where(Candidate.category_id == category_id)
        )
        candidates = result.scalars().all()

    # Формируем клавиатуру: одна кнопка на каждого кандидата
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{candidate.name} – {candidate.votes}",
                    callback_data=f"{role},candidates:{candidate.id}"
                )
            ]
            for candidate in candidates
        ]
    )
    return keyboard
