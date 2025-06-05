from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, CallbackQuery

from app.utils import filter_data

admin_rt = Router(name='admins')


def main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Toifalar', callback_data='admin-panel-categories')],
        [InlineKeyboardButton(text='Yordam', callback_data='admin-help')],
    ])


def categories_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='ENG FAOL YOSHLAR ISHLARI BO\'LIMI BOSHLIG\'I ', callback_data='categories:1')],
        [InlineKeyboardButton(text='Toifa 2', callback_data='categories:2')],
        [InlineKeyboardButton(text='Toifa 3', callback_data='categories:3')]
    ])


def candidates_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Kuziyev Behzod Bikmuratovich - 152', callback_data='candidates:1')],
        [InlineKeyboardButton(text='Nomzod2 - 0', callback_data='candidates:2')],
        [InlineKeyboardButton(text='Nomzod3 - 0', callback_data='candidates:3')]
    ])


@admin_rt.message(Command('start'))
async def handle_start(msg: Message):
    await msg.answer('Assolomu alaykum', reply_markup=main_kb())



@admin_rt.callback_query(F.data.contains('admin-panel-categories'))
async def categories_list(call: CallbackQuery):
    await call.bot.edit_message_text(text='Toifalar', message_id=call.message.message_id, chat_id=call.from_user.id,
                                     reply_markup=categories_kb())


@admin_rt.callback_query(F.data.startswith('categories:'))
async def candidates_list(call: CallbackQuery):
    category_id = filter_data(call.data, 'categories:')
    await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text='Toifa 1',
                                     reply_markup=candidates_kb())


