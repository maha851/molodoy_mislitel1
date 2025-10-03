from aiogram import F, types, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton,ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder


user_private_router = Router()


@user_private_router.message(CommandStart())
async def comand_start(message: types.Message):
    await message.answer("\u2063", reply_markup=ReplyKeyboardRemove())
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





@user_private_router.message(F.text == "/deltest")
async def deltest(m: types.Message):
    sent = await m.answer("Тест: это сообщение я попытаюсь удалить сразу")
    try:
        await m.bot.delete_message(sent.chat.id, sent.message_id)
        await m.answer("✅ Удалилось сразу")
    except TelegramBadRequest as e:
        await m.answer(f"❌ Не смог удалить: {e!r}")


@user_private_router.callback_query(lambda c: c.data == 'btn1')
async def process_callback_button1(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            # Первый ряд кнопок
            [
                InlineKeyboardButton(text="Выбрать ученика", callback_data="btn2")
            ]]
    )
#     await callback_query.message.answer('''<b>Способы оплаты</b>
# ✅ <b>Тинькофф (RUB):</b> по номеру +7 978 870-59-26 (Эльмаз)
# ✅ <b>Сбер (RUB):</b> по номеру +7 978 870-59-26 (Эльмаз)
# ✅ <b>Visa А-Банк (UAH):</b> 4323 3870 1031 9187
# ✅ <b>PayPal (EU/WW):</b> elzasadika@gmail.com — тип платежа <i>Friends and Family</i>
# ✅ <b>Турецкая карта (TRY):</b> IBAN TR23 0082 9000 0949 1147 3974 12 — Elmaz Zeitulaeva
# ℹ️ Сумма для оплаты была указана в родительском чате (или как вы договорились заранее).
# ℹ️ Конвертацию в удобную валюту производите самостоятельно.
# <b>Что конкретно сделать сейчас?</b>
#     1)Нажмите “выбрать ученика”
#     2)Введите 3 первые буквы его имени
#     3)Выберите из выдачи своего ребёнка
#     4)Выберите месяц(ы) за которые оплачиваете
#     5)Прикрепите скрин или же pdf файл об оплате
#       Всё!
    await callback_query.message.answer('''Способы оплаты:
 В рублях, на карту тинькофф: по номеру +7 978 870-59-26 (Эльмаз)
 В рублях, на карту Сбер: по номеру +7 978 870-59-26 (Эльмаз)
 В гривне, на карту Visa А-Банк (UAH): 4323 3870 1031 9187
 В долларах PayPal (EU/WW): elzasadika@gmail.com — тип платежа Friends and Family
 Турецкая лира: IBAN TR23 0082 9000 0949 1147 3974 12 — Elmaz Zeitulaeva
 Сумма для оплаты была указана в родительском чате (или как вы договорились заранее).
 Конвертацию в удобную валюту производите самостоятельно.
<b>Что конкретно сделать сейчас?</b>
    1)Нажмите “выбрать ученика”
    2)Введите 3 первые буквы его имени
    3)Выберите из выдачи своего ребёнка
    4)Выберите месяц(ы) за которые оплачиваете
    5)Прикрепите скрин или же pdf файл об оплате
      Всё!''',parse_mode='HTML',reply_markup=keyboard)
