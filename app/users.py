from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

user_rt = Router(name='users')


def start_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Kanalga obuna bo'lish", url='https://t.me/shohrux_yigitaliev')]
    ])


def vote_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Ovoz berish', callback_data='vote')],
        [InlineKeyboardButton(text='Yordam', callback_data='admin-help')],
    ])


@user_rt.message(Command('start'))
async def handle_start(msg: Message):
    await msg.answer('Assolomu alaykum', reply_markup=start_kb())
