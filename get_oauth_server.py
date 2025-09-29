import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Доступы (добавляй нужные)
SCOPES = ["https://www.googleapis.com/auth/drive"]

BASE_DIR = "/home/botuser/molodoy_mislitel1/creds/oauth.json"
OAUTH_PATH = os.path.join(BASE_DIR, "oauth.json")
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")

def get_creds():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Консольный поток — подходит для сервера без браузера
            flow = InstalledAppFlow.from_client_secrets_file(OAUTH_PATH, SCOPES)
            creds = flow.run_console()  # <-- тут выдаст ссылку и попросит вставить код

        # Сохраняем токен на будущее
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return creds

def main():
    creds = get_creds()
    drive = build("drive", "v3", credentials=creds)

    # Пример: вывести первые 10 файлов на Диске
    results = drive.files().list(pageSize=10, fields="files(id, name)").execute()
    files = results.get("files", [])
    for f in files:
        print(f'{f["name"]}  {f["id"]}')

if __name__ == "__main__":
    main()
