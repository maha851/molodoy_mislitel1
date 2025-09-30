from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton,ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder


user_private_router = Router()


@user_private_router.message(CommandStart())
async def comand_start(message: types.Message):
    await message.answer("", reply_markup=ReplyKeyboardRemove())
    first_name = message.from_user.first_name  # имя
    last_name = message.from_user.last_name  # фамилия (может быть None)
    username = message.from_user.username
    # await message.answer('',reply_markup=ReplyKeyboardRemove())
    keyboard = InlineKeyboardMarkup(
    inline_keyboard = [
        # Первый ряд кнопок
        [
            InlineKeyboardButton(text="Ok", callback_data="btn1")
        ]])
    await message.answer(f'''Ассаламу алейкум уа рахматуЛЛахи уа баракятух, {first_name}! 👋
    Я — бот-помощник для учёта оплат за учеников курса «Молодой мыслитель» 📚
     Важно: я не проверяю факт оплаты — я только ставлю отметку ✅, потому что мы доверяем вам 🤝
     Нажмите кнопку ниже, чтобы посмотреть способы оплаты 💳👇''',reply_markup=keyboard)



@user_private_router.callback_query(lambda c: c.data == 'btn1')
async def process_callback_button1(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            # Первый ряд кнопок
            [
                InlineKeyboardButton(text="Выбрать ученика", callback_data="btn2")
            ]]
    )
    await callback_query.message.answer('''Способы оплаты
 Тинькофф (RUB): по номеру +7 978 870-59-26 (Эльмаз)
 Сбер (RUB): по номеру +7 978 870-59-26 (Эльмаз)
 Visa А-Банк (UAH): 4323 3870 1031 9187
 PayPal (EU/WW): elzasadika@gmail.com — тип платежа Friends and Family
 Турецкая карта (TRY): IBAN TR23 0082 9000 0949 1147 3974 12 — Elmaz Zeitulaeva
 Сумма для оплаты была указана в родительском чате (или как вы договорились заранее).
 Конвертацию в удобную валюту производите самостоятельно.
Что конкретно сделать сейчас?
Нажмите “выбрать ученика”
Введите 3 первые буквы его имени
Выберите из выдачи своего ребёнка
Выберите месяц(ы) за которые оплачиваете
Прикрепите скрин об оплате
Всё!
''',parse_mode='HTML',reply_markup=keyboard)