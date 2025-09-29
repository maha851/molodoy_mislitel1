# google_drive_auth.py
from __future__ import annotations

import json
import os
import pathlib
from typing import Iterable, Optional

from dotenv import find_dotenv, load_dotenv
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials as UserCreds, Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

load_dotenv(find_dotenv())

Outh=os.getenv('Outh')
token=os.getenv('token')

DEFAULT_SCOPES = ["https://www.googleapis.com/auth/drive.file"]
DEFAULT_CREDS_FILE = os.getenv(Outh) or "/home/botuser/molodoy_mislitel1/creds/oauth.json"
DEFAULT_TOKEN_FILE = os.getenv(token)  or "/home/botuser/molodoy_mislitel1/creds/token.json"
       # создастся автоматически после 1-го входа

RUN_ON_SERVER = os.getenv("RUN_ON_SERVER", "0").lower() in ("1", "true")

def _load_client_config(creds_file: str) -> dict:
    """Берём client_secret (oauth.json) из ENV (если задан JSON) или с диска."""
    inline = os.getenv("GOOGLE_OAUTH_CLIENT_JSON")
    if Outh:
        return json.loads(Outh)
    p = pathlib.Path(creds_file)
    if not p.exists():
        raise FileNotFoundError(f"OAuth client file not found: {creds_file}")
    return json.loads(p.read_text(encoding="utf-8"))

def get_creds(
    scopes: Optional[Iterable[str]] = None,
    creds_file: str = DEFAULT_CREDS_FILE,
    token_file: str = DEFAULT_TOKEN_FILE,
) -> Credentials:
    """
    Возвращает валидные OAuth-учётные данные (Credentials).
    Если token_file существует — подхватывает; иначе запускает браузер для логина.
    """
    creds_file = DEFAULT_CREDS_FILE
    token_file = DEFAULT_TOKEN_FILE
    scopes = list(scopes or DEFAULT_SCOPES)

    if not isinstance(token_file, str) or not token_file:
        raise ValueError("GOOGLE_OAUTH_TOKEN/DEFAULT_TOKEN_FILE не задан: ожидается строка-путь к token.json")
    if not isinstance(creds_file, str) or not creds_file:
        raise ValueError("GOOGLE_OAUTH_CLIENT/DEFAULT_CREDS_FILE не задан: ожидается строка-путь к oauth.json")

    creds: Optional[UserCreds] = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if RUN_ON_SERVER:
                # На сервере не пытаемся открывать браузер
                raise RuntimeError(
                    "Нет валидного token.json на сервере. "
                    "Сделайте локально авторизацию (без RUN_ON_SERVER), получите token.json и загрузите его на сервер "
                    f"в путь: {token_file}"
                )
            # Локальная машина — разрешаем интерактив
            client_config = _load_client_config(creds_file)
            flow = InstalledAppFlow.from_client_config(client_config, scopes=scopes)
            creds = flow.run_local_server(port=0)
            with open(token_file, "w", encoding="utf-8") as f:
                f.write(creds.to_json())

    return creds

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
