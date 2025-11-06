import os
from io import BytesIO

import requests
from dotenv import load_dotenv, find_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from sqlalchemy.util import await_only

from aiogram import Router, F, Bot
from aiogram.types import Message

load_dotenv(find_dotenv())


HidenCat=os.getenv('HidenCat')
Outh = os.getenv('outh')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDS = service_account.Credentials.from_service_account_file(HidenCat, scopes=SCOPES)
service = build('sheets', 'v4', credentials=CREDS)
SPREADSHEET_ID = '1YbHyUySI6IAymP8QlF1-w4Z02ibqQWhLUOmWZNNN96c'
SHEET_NAME = 'Ученики'





def read_sheet(range_name="A1:D100"):
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name
    ).execute()
    return result.get('values', [])



router = Router()


def col_to_letters(n: int) -> str:
    """Преобразует номер столбца (1 -> A, 27 -> AA)"""
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

def mark_payment(user_name: str, month: str):
    norm = lambda s: s.strip().lower()

    # 1. Заголовки (первая строка)
    header_res = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A1:ZZ1"
    ).execute()
    header = header_res.get("values", [[]])[0]

    try:
        col_index_1based = next(i+1 for i, h in enumerate(header) if norm(h) == norm(month))
    except StopIteration:
        raise ValueError(f"Месяц «{month}» не найден в заголовке: {header}")

    # 2. Первый столбец (имена детей)
    users_res = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!B2:B"   # смотри, у тебя имена в колонке B
    ).execute()
    users_col = [row[0] for row in users_res.get("values", []) if row]

    try:
        row_index_1based = users_col.index(user_name) + 2  # +2: смещение, так как данные с B2
    except ValueError:
        raise ValueError(f"Ребёнок «{user_name}» не найден в таблице.")

    # 3. Ячейка для обновления
    col_letters = col_to_letters(col_index_1based)
    cell_a1 = f"{SHEET_NAME}!{col_letters}{row_index_1based}"

    # 4. Записываем галочку
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=cell_a1,
        valueInputOption="USER_ENTERED",
        body={"values": [["✅"]]}
    ).execute()

    return cell_a1
