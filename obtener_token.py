"""Ejecútalo UNA vez por canal en tu PC para autorizar la subida.

  python obtener_token.py          -> canal de historia oscura  (credenciales_youtube.txt, variables YT_*)
  python obtener_token.py civ      -> canal de civilizaciones   (credenciales_youtube_civ.txt, variables YT_CIV_*)

Necesita client_secret.json (cliente OAuth "Aplicación de escritorio") en esta carpeta.
Se abre el navegador: entra con la cuenta del canal y, si pregunta, ELIGE EL CANAL CORRECTO.
Copia las 3 líneas del .txt en las variables de entorno de la nube y luego borra el .txt.
"""
import json, sys
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.readonly"]

canal = sys.argv[1].lower() if len(sys.argv) > 1 else ""
prefijo = f"YT_{canal.upper()}_" if canal else "YT_"
salida = f"credenciales_youtube_{canal}.txt" if canal else "credenciales_youtube.txt"

aqui = Path(__file__).parent
flow = InstalledAppFlow.from_client_secrets_file(str(aqui / "client_secret.json"), SCOPES)
creds = flow.run_local_server(port=0, prompt="consent select_account", access_type="offline")
cfg = json.loads((aqui / "client_secret.json").read_text())["installed"]
(aqui / salida).write_text(
    f"{prefijo}CLIENT_ID={cfg['client_id']}\n{prefijo}CLIENT_SECRET={cfg['client_secret']}\n"
    f"{prefijo}REFRESH_TOKEN={creds.refresh_token}\n", encoding="utf-8")
print(f"Listo: credenciales guardadas en {salida} (no lo subas a GitHub).")
