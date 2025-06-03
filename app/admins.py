from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

admin_rt = Router(name='admins')

def main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Admin Panel', callback_data='admin-panel')],
        [InlineKeyboardButton(text='Yordam', callback_data='admin-help')],
    ])

@admin_rt.message(Command('start'))
async def handle_start(msg: Message):
    await msg.answer('Assolomu alaykum', reply_markup=main_kb())

