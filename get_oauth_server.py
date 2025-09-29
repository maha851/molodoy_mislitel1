import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]

# Берём из окружения или ставим дефолт
raw_path = os.getenv("OAUTH_PATH", "/home/botuser/molodoy_mislitel1/creds/oauth.json")

# Если дали директорию — добавим имя файла; если дали .json — используем как есть
OAUTH_PATH = os.path.join(raw_path, "oauth.json") if os.path.isdir(raw_path) else raw_path

assert os.path.isfile(OAUTH_PATH), f"OAuth client file not found: {OAUTH_PATH}"

flow = InstalledAppFlow.from_client_secrets_file(OAUTH_PATH, SCOPES)
creds = flow.run_console()
