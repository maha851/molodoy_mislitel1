import asyncio

from aiogram import F, types, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton,ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from common.bot_comands_list import delete_later

user_private_router = Router()


@user_private_router.message(CommandStart())
async def comand_start(message: types.Message):
    await message.answer("\u2063", reply_markup=ReplyKeyboardRemove())
    first_name = message.from_user.first_name  # имя
    # await message.answer('',reply_markup=ReplyKeyboardRemove())
    keyboard = InlineKeyboardMarkup(
    inline_keyboard = [
        # Первый ряд кнопок
        [
            InlineKeyboardButton(text="Ok", callback_data="btn1")
        ]])
    sent = await message.answer(f'''Ассаламу алейкум уа рахматуЛЛахи уа баракятух, {first_name}! 👋
    Я — бот-помощник для учёта оплат за учеников курса «Молодой мыслитель» 📚
     Важно: я не проверяю факт оплаты — я только ставлю отметку ✅, потому что мы доверяем вам 🤝
     Нажмите кнопку ниже, чтобы посмотреть способы оплаты 💳👇''',reply_markup=keyboard)
    asyncio.create_task(delete_later(message, delay=24 * 3600))
    asyncio.create_task(delete_later(sent, delay=24 * 3600))

@user_private_router.callback_query(lambda c: c.data == 'btn1')
async def process_callback_button1(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            # Первый ряд кнопок
            [
                InlineKeyboardButton(text="Выбрать ученика", callback_data="btn2")
            ]]
    )
    sent = await callback_query.message.answer('''По способам оплаты: 
✅ На карту в рублях +79101404458 сбербанк (Сафие)
✅ В гривне на карту Visa АБанка 4323387010319187    
✅Для жителей Европы есть возможность оплаты на карту PayPal elzasadika@gmail.com тип платежа Friend and family . 
✅На турецкую карту в лирах TR94 0001 0090 1105 6013 4050 01   Elmaz Zeitulaeva

 Сумма для оплаты была указана в родительском чате (или как вы договорились заранее).
Конвертировать рубли в удобную для вас валюту нужно самостоятельно на момент оплаты.
<b>Что конкретно сделать сейчас?</b>
    1)Нажмите “выбрать ученика”
    2)Введите 3 первые буквы его имени
    3)Выберите из выдачи своего ребёнка
    4)Выберите месяц(ы) за которые оплачиваете
    5)Прикрепите скрин или же pdf файл об оплате
      Всё!''',parse_mode='HTML',reply_markup=keyboard)
    asyncio.create_task(delete_later(callback_query.message, delay=24 * 3600))
    asyncio.create_task(delete_later(sent, delay=24 * 3600))
