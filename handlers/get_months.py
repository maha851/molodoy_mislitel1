# aiogram 3.x
from aiogram import Router, F, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from get_students.get_stdnts import Form

photo_router  = Router()

# ----- FSM -----


# ----- Константы -----
MONTHS = [
    "Январь", "Февраль", "Март", "Апрель",
    "Май", "Июнь", "Июль", "Август",
    "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
]

BTN_DONE     = "✅ Готово"
BTN_CLEAR    = "🗑 Очистить"
BTN_CANCEL   = "❌ Отмена"
CANCEL_ALIASES = {"❌ отмена", "отмена"}

VARIATION_SELECTOR = "\ufe0f"

def norm(s: str) -> str:
    # убираем вариационные селекторы и лишние пробелы, понижаем регистр
    return (s or "").replace(VARIATION_SELECTOR, "").strip().casefold()

# ----- Клавиатура -----
def months_reply_kb() -> ReplyKeyboardMarkup:
    # Сделаем по 3 месяца в строке
    rows = []
    row = []
    for i, m in enumerate(MONTHS, start=1):
        row.append(KeyboardButton(text=m))
        if i % 3 == 0:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    # служебные кнопки
    rows.append([KeyboardButton(text=BTN_DONE)])
    rows.append([KeyboardButton(text=BTN_CLEAR), KeyboardButton(text=BTN_CANCEL)])

    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        input_field_placeholder="Выбирайте месяц(ы) и нажмите «Готово»"
    )

# ----- Старт выбора -----

@photo_router.message(Form.waiting_for_child)  # альтернативная команда
async def start_months(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    name = message.text
    await state.update_data(selected=[])
    await message.answer(
        "Выберите месяц(ы) для оплаты. Нажимайте по одному. Когда закончите — «✅ Готово».",
        reply_markup=months_reply_kb()
    )

    await state.set_state(Form.waiting_for_month)

# ----- Обработка нажатий на кнопки во время выбора -----


@photo_router.message(F.text.func(lambda t: norm(t) in CANCEL_ALIASES))
async def cancel_anywhere(message: types.Message, state: FSMContext):
    await message.answer("Отменено.", reply_markup=ReplyKeyboardRemove())
    await state.clear()

@photo_router.message(Form.waiting_for_month)
async def handle_choice(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()

    # отмена
    if text == BTN_CANCEL:
        await message.answer("Отменено.", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return

    # очистить выбор
    if text == BTN_CLEAR:
        await state.update_data(selected=[])
        await message.answer("Список очищен. Выбирайте заново.")
        return

    # завершить выбор
    if text == BTN_DONE:
        data = await state.get_data()
        selected = data.get("selected", [])
        if not selected:
            await message.answer("❗ Нужен хотя бы один месяц.")
            return
        # НЕ очищаем state здесь — чтобы следующие хендлеры (фото/PDF) могли взять месяцы
        await message.answer(
            f"Вы выбрали: {', '.join(selected)}.\nТеперь отправьте фото или PDF с оплатой 📎",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(Form.waiting_for_photo)
        return

    # выбор месяца (тоггл)
    if text in MONTHS:
        data = await state.get_data()
        selected = data.get("selected", [])

        if text in selected:
            selected.remove(text)
            msg = f"Удалил «{text}» из списка."
        else:
            selected.append(text)
            msg = f"Добавил «{text}»."

        # нормализуем порядок по MONTHS
        selected_sorted = [m for m in MONTHS if m in selected]
        await state.update_data(selected=selected_sorted)

        pretty = ", ".join(selected_sorted) if selected_sorted else "пока пусто"
        await message.answer(f"{msg}\nТекущий выбор: {pretty}\nКогда закончите — нажмите «{BTN_DONE}».")
        return

    # любое другое сообщение
    await message.answer("Пожалуйста, выберите месяц(ы) с клавиатуры или нажмите «✅ Готово».")
