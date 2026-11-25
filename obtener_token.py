"""Ejecútalo UNA vez en tu PC para autorizar la subida al canal.

1. Descarga el JSON del cliente OAuth (tipo "Aplicación de escritorio") de Google Cloud
   y guárdalo en esta carpeta como client_secret.json
2. python -m pip install google-auth-oauthlib
3. python obtener_token.py   -> se abre el navegador, entra con la cuenta del canal y acepta
4. Abre credenciales_youtube.txt y copia los 3 valores en las variables de entorno
   del entorno de la nube. Luego borra ese archivo y client_secret.json.
"""
import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.readonly"]

aqui = Path(__file__).parent
flow = InstalledAppFlow.from_client_secrets_file(str(aqui / "client_secret.json"), SCOPES)
creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")
cfg = json.loads((aqui / "client_secret.json").read_text())["installed"]
(aqui / "credenciales_youtube.txt").write_text(
    f"YT_CLIENT_ID={cfg['client_id']}\nYT_CLIENT_SECRET={cfg['client_secret']}\nYT_REFRESH_TOKEN={creds.refresh_token}\n",
    encoding="utf-8")
print("Listo: credenciales guardadas en credenciales_youtube.txt (no lo subas a GitHub).")
