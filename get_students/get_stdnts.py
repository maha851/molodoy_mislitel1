from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from database import data_names
from database import mark_payment


def proverka(frist_leters:str):
    for name in data_names:
        if frist_leters.lower() in name.lower():
            return True
    return False



def keyboard_from_students(frist_leters):
    builder = ReplyKeyboardBuilder()

    # Добавляем кнопки с именами (по 2 в ряд)
    for name in data_names:
        if frist_leters.lower() in name.lower():
            count = True
            builder.add(KeyboardButton(text=name))

    # Добавляем кнопку отмены
    builder.add(KeyboardButton(text="❌ Отмена"))

    # Форматируем в сетку 2 колонки
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


get_students_list_router = Router()
class Form(StatesGroup):
    waiting_for_name_letters = State()
    waiting_for_child = State()
    waiting_for_month = State()



def get_months_keyboard():
    builder = ReplyKeyboardBuilder()

    months = [
        "Январь", "Февраль", "Март",
        "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь",
        "Октябрь", "Ноябрь", "Декабрь"
    ]

    for i in months:
        builder.add(KeyboardButton(text=i))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


@get_students_list_router.callback_query(lambda c: c.data == 'btn2')
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_for_name_letters)
    await callback_query.message.answer('Введите первые три буквы имени вашего ученика:')

@get_students_list_router.message(Form.waiting_for_name_letters)
async def process_name_letters(message: types.Message, state: FSMContext):
    user_input = message.text.strip()
    if len(user_input) == 3 and proverka(user_input):
        await state.set_state(Form.waiting_for_child)
        keyboard = keyboard_from_students(user_input)
        await message.answer('выберите вашего ученика:', reply_markup=keyboard)
    elif len(user_input) != 3:
        await message.answer('длинна введённого сообщения не равняется трём')
    elif not proverka(user_input):
        await message.answer(f'ученика, имя которого начинается на {user_input} нет.Попробуйте ввести сново')



@get_students_list_router.message(Form.waiting_for_child)
async def choose_child(message: types.Message, state: FSMContext):
        # сохраняем выбор
    await state.update_data(name=message.text)
    name = message.text
    await message.answer(f"Вы выбрали: {name}\nТеперь выберите месяц:",
                         reply_markup=get_months_keyboard())
    await state.set_state(Form.waiting_for_month)

@get_students_list_router.message(Form.waiting_for_month)
async def choose_month(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data["name"]  # имя ребёнка
    month = message.text
    await message.answer(f"✅ Оплата за {month} для {name} зарегистрирована!",reply_markup=ReplyKeyboardRemove())
    mark_payment(name,month.lower())
    await state.clear()