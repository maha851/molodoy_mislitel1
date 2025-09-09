from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


user_private_router = Router()


@user_private_router.message(CommandStart())
async def comand_start(message: types.Message):
    first_name = message.from_user.first_name  # имя
    last_name = message.from_user.last_name  # фамилия (может быть None)
    username = message.from_user.username
    keyboard = InlineKeyboardMarkup(
    inline_keyboard = [
        # Первый ряд кнопок
        [
            InlineKeyboardButton(text="Ok", callback_data="btn1")
        ]])
    await message.answer(f'''Ассаламу алейкум уа рахматуЛЛахи уа баракятух, {first_name} {last_name} or {username}! 👋
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
    await callback_query.message.answer('''<b>Способы оплаты</b>
✅ <b>Тинькофф (RUB):</b> по номеру +7 978 870-59-26 (Эльмаз)
✅ <b>Сбер (RUB):</b> по номеру +7 978 870-59-26 (Эльмаз)
✅ <b>Visa А-Банк (UAH):</b> 4323 3870 1031 9187
✅ <b>PayPal (EU/WW):</b> elzasadika@gmail.com — тип платежа <i>Friends and Family</i>
✅ <b>Турецкая карта (TRY):</b> IBAN TR23 0082 9000 0949 1147 3974 12 — Elmaz Zeitulaeva
ℹ️ Сумма для оплаты была указана в родительском чате (или как вы договорились заранее).
ℹ️ Конвертацию в удобную валюту производите самостоятельно.
''',parse_mode='HTML',reply_markup=keyboard)