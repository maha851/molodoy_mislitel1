from fileinput import filename

import requests
from io import BytesIO
from datetime import datetime

from dotenv import find_dotenv, load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os, pickle

from database.database import Outh
from photo_operation.google_drive_auth import get_drive

drive = get_drive()


load_dotenv(find_dotenv())

DEFAULT_SCOPES = ["https://www.googleapis.com/auth/drive.file"]
DEFAULT_CREDS_FILE = os.getenv('outH') or "/home/botuser/molodoy_mislitel1/creds/oauth.json"
DEFAULT_TOKEN_FILE = os.getenv('token') or "/home/botuser/molodoy_mislitel1/creds/token.json"

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


creds = None
if os.path.exists("token.pickle"):
    with open("token.pickle", "rb") as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(DEFAULT_CREDS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
    with open("token.pickle", "wb") as token:
        pickle.dump(creds, token)

drive = build("drive", "v3", credentials=creds)


def download_telegram_file(bot_token: str, file_id: str) -> tuple[BytesIO, str]:
    """
    Скачивает файл из Telegram по file_id.
    Возвращает (buf, ext):
        buf — BytesIO с содержимым файла
        ext — расширение файла (например: 'jpg', 'png', 'pdf')
    """

    # 1) Узнаем путь к файлу
    r = requests.get(
        f"https://api.telegram.org/bot{bot_token}/getFile",
        params={"file_id": file_id},
        timeout=30
    )
    r.raise_for_status()
    file_path = r.json()["result"]["file_path"]

    # 2) Скачиваем байты
    file_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
    resp = requests.get(file_url, timeout=60)
    resp.raise_for_status()

    buf = BytesIO(resp.content)
    buf.seek(0)

    # 3) Определяем расширение
    ext = (file_path.split(".")[-1] or "jpg").lower()
    if len(ext) > 5 or "/" in ext:  # защита от кривого имени
        ext = "jpg"

    return buf, ext



def upload_to_google_drive(drive, buf: BytesIO, ext: str, folder_id: str, filename: str | None = None,) -> str:
    """
    Загружает файл в Google Диск.
    drive — build("drive", "v3", credentials=creds)
    buf   — BytesIO с содержимым файла
    ext   — расширение ('jpg', 'png', 'pdf' и т.п.)
    folder_id — ID папки (или None, если в корень)
    """

    # Имя файла
    name = filename

    # Метаданные
    meta = {"name": name}
    if folder_id:
        meta["parents"] = [folder_id]

    # Загружаем
    mime = f"image/{'jpeg' if ext == 'jpg' else ext}"
    media = MediaIoBaseUpload(buf, mimetype=mime, resumable=False)
    created = drive.files().create(body=meta, media_body=media, fields="id,webViewLink").execute()

    return created["webViewLink"]