from google.oauth2 import service_account
from googleapiclient.discovery import build
from sqlalchemy.util import await_only

from aiogram import Router, F
from aiogram.types import Message

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDS = service_account.Credentials.from_service_account_file('/home/ahma/Загрузки/hidden-cat-470607-a5-7611437960ad.json', scopes=SCOPES)
service = build('sheets', 'v4', credentials=CREDS)
SPREADSHEET_ID = '1YbHyUySI6IAymP8QlF1-w4Z02ibqQWhLUOmWZNNN96c'

def read_sheet(range_name="A1:D100"):
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name
    ).execute()
    return result.get('values', [])

async def show_data():
    data = await read_sheet()
    return data



router = Router()

data = read_sheet()

data_names = []

for i in data[1:len(data)//2]:
    data_names.append(i[1])


@router.message(F.text == "asaaaa")
async def show_data(message: Message):

    if not data:
        await message.answer("Нет данных")
        return

    response = "📊 Данные из таблицы:\n\n"
    for row in sorted(data_names):
        response += row + '\n'


    await message.answer(response)