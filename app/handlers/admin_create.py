from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, CallbackQuery, InlineKeyboardButton, Message
from sqlalchemy.ext.asyncio import async_session
from sqlalchemy.orm import selectinload

from app.config import bot
from app.data.database import async_session  # оставлен единственный импорт из вашего модуля
from app.data.models import Category, Candidate
from app.data.repository import CategoryRepository, CandidateRepository
from app.middleware.check_admin import AdminOnlyMiddleware
from app.schemas import CategoryCreate, CreateCandidate
from app.states import VotesStates
from app.utils import filter_data

admin_create_rt = Router(name='admin_create')
admin_create_rt.message.middleware(AdminOnlyMiddleware())


def manage_new_category_kb(cat_id: int, run_vote_btn: bool = False, check_btn: bool = False) -> InlineKeyboardMarkup:
    """
    Клавиатура для управления голосованием:
    - Добавить кандидата
    - Запустить голосование (если run_vote_btn=True)
    - Проверить категорию (если check_btn=True)
    """
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
                text="Ovoz berishni ishga tushirish",
                callback_data=f"new-vote,run,category:{cat_id}"
            )
        )

    # Размещаем каждую кнопку в отдельном ряду
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[btn] for btn in buttons])
    return keyboard


# ------------------------------
# Хендлеры на команды
# ------------------------------

@admin_create_rt.message(Command('new_category'))
async def create_votes(msg: Message, state: FSMContext):
    """
    Шаг 1: Просим ввести название категории (чтобы создать новую категорию голосования).
    """
    msg1 = await msg.answer(
        "TOIFA NOMI: -\n"
        "Nomzodlar soni: 0"
    )
    msg2 = await msg.answer(
        "Toifa nomini kiriting!\n"
        "Bekor qilish: /break"
    )

    await state.update_data(msg1=msg1.message_id, msg2=msg2.message_id)
    await state.set_state(VotesStates.get_category_title)


@admin_create_rt.message(StateFilter(VotesStates.get_category_title))
async def add_title(msg: Message, state: FSMContext):
    """
    Шаг 2: Создаём категорию, удаляем вспомогательные сообщения, редактируем текст
    с кнопкой для добавления кандидатов.
    """
    data = await state.get_data()
    msg1_id = data.get('msg1')
    msg2_id = data.get('msg2')

    # Если пользователь ввёл 'break' => отмена
    if 'break' in msg.text:
        await state.clear()
        await msg.answer('Bekor qilindi')
        return

    title = msg.text
    async with async_session() as session:
        repo = CategoryRepository(Category, session)
        category_schema = CategoryCreate(title=title)
        category = await repo.create(category_schema)

    # Удаляем ввод пользователя и сообщение с подсказкой
    await bot.delete_message(chat_id=msg.from_user.id, message_id=msg2_id)
    await bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id)

    # Редактируем первое сообщение на название категории + кнопка
    await bot.edit_message_text(
        chat_id=msg.from_user.id,
        message_id=msg1_id,
        text=f"{title}\nNomzodlar soni: 0",
        reply_markup=manage_new_category_kb(cat_id=category.id)
    )

    await state.clear()


@admin_create_rt.callback_query(F.data.startswith('new-vote,add-candidate,category:'))
async def answer(call: CallbackQuery, state: FSMContext):
    """
    Шаг 3: Нажали "Nomzod qo'shish" => просим ввести имя кандидата.
    """
    category_id = filter_data(call.data, 'new-vote,add-candidate,category:')
    await state.update_data(category_id=category_id)

    msg2 = await call.message.answer(
        "Nomzodni kiriting:\n"
        "Bekor qilish: /break"
    )

    await state.update_data(
        msg1_id=call.message.message_id,
        msg2_id=msg2.message_id
    )
    await state.set_state(VotesStates.get_candidate)


@admin_create_rt.message(StateFilter(VotesStates.get_candidate))
async def add_candidate(msg: Message, state: FSMContext):
    """
    Шаг 4: Получаем имя кандидата, сохраняем в БД,
    считаем кол-во кандидатов и обновляем текст с кнопками.
    """
    if 'break' in msg.text:
        await state.clear()
        await msg.answer('Bekor qilindi')
        return

    state_data = await state.get_data()
    category_id = state_data.get('category_id')
    msg1_id = state_data.get('msg1_id')
    msg2_id = state_data.get('msg2_id')
    name = msg.text

    async with async_session() as session:
        candidate_repo = CandidateRepository(Candidate, session)
        schema = CreateCandidate(name=name, category_id=category_id)
        await candidate_repo.create(schema)

        # Подгружаем категорию с кандидатами, чтобы узнать текущее их число
        category = await session.get(
            Category,
            category_id,
            options=[selectinload(Category.candidates)]
        )
        candidates_count = len(category.candidates)

    # Удаляем сообщение с вводом и скрываем сообщение-хвост
    await msg.delete()
    try:
        await bot.delete_message(chat_id=msg.from_user.id, message_id=msg2_id)
    except Exception:
        pass

    # Обновляем сообщение с названием категории и клавиатуру
    await bot.edit_message_text(
        chat_id=msg.from_user.id,
        message_id=msg1_id,
        text=f"{category.title}\nNomzodlar soni: {candidates_count}",
        reply_markup=manage_new_category_kb(
            cat_id=category_id,
            check_btn=True,
            run_vote_btn=True
        )
    )

    await state.clear()


