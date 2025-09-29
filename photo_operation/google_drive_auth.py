# google_drive_auth.py
from __future__ import annotations
import os
from typing import Iterable, Optional

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from database.database import Outh

DEFAULT_SCOPES = ["https://www.googleapis.com/auth/drive.file"]
DEFAULT_CREDS_FILE = Outh  # скачиваете из GCP (OAuth Client ID → Desktop App)
DEFAULT_TOKEN_FILE = "token.json"        # создастся автоматически после 1-го входа


def get_creds(
    scopes: Optional[Iterable[str]] = None,
    creds_file: str = DEFAULT_CREDS_FILE,
    token_file: str = DEFAULT_TOKEN_FILE,
) -> Credentials:
    """
    Возвращает валидные OAuth-учётные данные (Credentials).
    Если token_file существует — подхватывает; иначе запускает браузер для логина.
    """
    scopes = list(scopes or DEFAULT_SCOPES)

    creds: Optional[Credentials] = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Откроет окно авторизации в браузере
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, scopes)
            creds = flow.run_local_server(port=0)

        # Сохраняем токен, чтобы не логиниться каждый раз
        with open(token_file, "w") as f:
            f.write(creds.to_json())

    return creds


def get_drive(
    scopes: Optional[Iterable[str]] = None,
    creds_file: str = DEFAULT_CREDS_FILE,
    token_file: str = DEFAULT_TOKEN_FILE,
):
    """
    Возвращает авторизованный клиент Google Drive API (v3).
    """
    creds = get_creds(scopes=scopes, creds_file=creds_file, token_file=token_file)
    return build("drive", "v3", credentials=creds)
