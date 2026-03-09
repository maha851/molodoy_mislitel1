import asyncio
import os
from fileinput import filename
from io import BytesIO

from aiogram import Router, types, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardRemove, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv, find_dotenv

from common.bot_comands_list import delete_later
from database.database import read_sheet
from database.database import mark_payment
from photo_operation.google_drive_auth import get_drive
from photo_operation.operation_with_photo import download_telegram_file, upload_to_google_drive, drive
load_dotenv(find_dotenv())

phone_number = '+79788705926'
TOKEN=os.getenv('TOKEN')

FOLDER_ID = '1ymw4Avo1HWhBrtYt_mlN4E6Is9KVFo2-'

drive = get_drive()




def keyboard_from_students(frist_leters):
    builder = ReplyKeyboardBuilder()
    data = read_sheet()

    data_names = []

    for i in data[1:len(data)]:
        data_names.append(i[1])

    # Добавляем кнопки с именами (по 2 в ряд)
    for name in data_names:
        if frist_leters.lower() in name.lower():
            builder.add(KeyboardButton(text=name))

    # Добавляем кнопку отмены
    builder.add(KeyboardButton(text="❌ Отмена"))

    # Форматируем в сетку 2 колонки
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True)


get_students_list_router = Router()

class Form(StatesGroup):
    waiting_for_name_letters = State()
    waiting_for_child = State()
    waiting_for_month = State()
    waiting_for_photo = State()



@get_students_list_router.callback_query(lambda c: c.data == 'btn2')
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_for_name_letters)
    sent = await callback_query.message.answer('Наберите первые три буквы имени вашего ученика русскими буквами и отправьте сюда,\nесли в семье учатся два ребёнка, их имена будут со знаком +')
    asyncio.create_task(delete_later(callback_query.message, delay=24 * 3600))
    asyncio.create_task(delete_later(sent, delay=24 * 3600))


@get_students_list_router.message(F.text == '❌ Отмена')
async def otmena(message: types.Message):
    sent = await message.answer('Отменено\nесли хотите начать заного нажмите команду /start',reply_markup=ReplyKeyboardRemove())
    asyncio.create_task(delete_later(message, delay=24 * 3600))
    asyncio.create_task(delete_later(sent, delay=24 * 3600))


@get_students_list_router.message(Form.waiting_for_name_letters)
async def process_name_letters(message: types.Message, state: FSMContext):
    user_input = message.text.strip()
    data = read_sheet()

    data_names = []

    for i in data[1:len(data)]:
        data_names.append(i)
        await message.answer(data_names)
        await message.answer(data)

    def proverka(frist_leters: str):
        for name in data_names:
            if frist_leters.lower() in name.lower():
                return True
        return False
    sent = None
    if len(user_input) == 3 and proverka(user_input):
        await state.set_state(Form.waiting_for_child)
        keyboard = keyboard_from_students(user_input)
        sent = await message.answer('выберите вашего ученика:', reply_markup=keyboard)
    elif len(user_input) != 3:
        sent = await message.answer('длинна введённого сообщения не равняется трём')
    elif not proverka(user_input):
        sent = await message.answer(f'''Ученика, имя которого начинается на {user_input} нету в списках учеников.
    Если вы неправильно ввели первые три буквы имени вашего ученика,нажмите /start чтобы начать процесс оплаты заново.
    Но если вы всё правильно ввели, то напишите  на Whatsapp {phone_number}
     или в родительскую группу, откуда вы попали сюда, и мы всё починим 🙂''')
        await state.set_state(None)
    asyncio.create_task(delete_later(message, delay=24 * 3600))
    asyncio.create_task(delete_later(sent, delay=24 * 3600))



@get_students_list_router.message(Form.waiting_for_photo,F.photo)
async def wait_photo(message: types.Message,state: FSMContext):
    data = await state.get_data()
    name = data["name"]
    month = data['selected']
    file_id = message.photo[-1].file_id
    buf, ext = download_telegram_file(TOKEN, file_id)
    filename = f"Оплата_от_{name} за {month}.{ext}"
    filename1 = f"Вы оплатиле за {name} за {month}"
    upload_to_google_drive(drive, buf, ext, FOLDER_ID,filename)
    await message.answer(f'''ДжазакиЛлаха хайран за оплату! 🌟{filename1}
Я ещё совсем молодой и могу ошибаться. Если что-то пошло не так, 
напишите на Whatsapp +79788705926 или в родительскую группу, откуда вы попали сюда, и мы всё починим 🙂''')
    for i in month:
        mark_payment(name,i.lower())
    await state.clear()
    asyncio.create_task(delete_later(message, delay=24 * 3600))

@get_students_list_router.message(F.document & (F.document.mime_type == "application/pdf"))
async def upload_pdf(message: types.Message, bot,state: FSMContext):
    data = await state.get_data()
    name = data["name"]
    month = data['selected']
    # скачиваем документ в память
    buf = BytesIO()
    await bot.download(message.document, destination=buf)
    buf.seek(0)
    # вытаскиваем расширение
    ext = "pdf"
    filename = f"Оплата_от_{name} за {month}.{ext}"
    # грузим в диск
    upload_to_google_drive(drive, buf, ext, FOLDER_ID,filename)
    await message.answer(f"✅ оплата успешно прошла!")
    for i in month:
        mark_payment(name, i.lower())
    asyncio.create_task(delete_later(message, delay=24 * 3600))
    await state.clear()
