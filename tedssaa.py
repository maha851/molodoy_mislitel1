# auth_local.py
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/drive.file"]  # как в проде
CREDS_FILE = "/home/botuser/molodoy_mislitel1/creds/oauth.json"                                # путь к вашему client_secret

flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
creds: Credentials = flow.run_local_server(port=0)       # откроет браузер
with open("token.json", "w", encoding="utf-8") as f:
    f.write(creds.to_json())
print("✔ token.json создан")
