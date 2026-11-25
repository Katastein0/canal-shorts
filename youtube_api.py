"""Sube Shorts y lista los vídeos del canal con la API de YouTube.

Credenciales por variables de entorno (nunca en el repo):
  YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN

Uso:
  python youtube_api.py subir salida/<slug>          # sube short.mp4 con metadata del episodio
  python youtube_api.py listar                       # títulos ya publicados (para no repetir temas)
"""
import json, os, sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.readonly"]


def client():
    faltan = [v for v in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN") if not os.environ.get(v)]
    if faltan:
        sys.exit(f"Faltan variables de entorno: {', '.join(faltan)}")
    creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"],
                        client_id=os.environ["YT_CLIENT_ID"], client_secret=os.environ["YT_CLIENT_SECRET"],
                        token_uri="https://oauth2.googleapis.com/token", scopes=SCOPES)
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def subir(carpeta):
    carpeta = Path(carpeta)
    slug = carpeta.name
    ep = json.loads((Path(__file__).parent / "episodios" / f"{slug}.json").read_text(encoding="utf-8"))
    body = {
        "snippet": {"title": ep["title"][:100], "description": ep["description"],
                    "tags": ep["tags"], "categoryId": "27", "defaultLanguage": "es",
                    "defaultAudioLanguage": "es"},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False,
                   "containsSyntheticMedia": True},
    }
    yt = client()
    media = MediaFileUpload(str(carpeta / "short.mp4"), mimetype="video/mp4", resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    vid = resp["id"]
    estado = yt.videos().list(part="status", id=vid).execute()["items"][0]["status"]["privacyStatus"]
    print(f"SUBIDO https://youtube.com/shorts/{vid}  visibilidad={estado}")
    if estado != "public":
        print("AVISO: YouTube lo ha dejado en privado (proyecto de API sin auditar). Hay que hacerlo público a mano en Studio.")


def listar():
    yt = client()
    ch = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    token = None
    while True:
        r = yt.playlistItems().list(part="snippet", playlistId=uploads, maxResults=50, pageToken=token).execute()
        for it in r["items"]:
            print(it["snippet"]["publishedAt"][:10], it["snippet"]["title"])
        token = r.get("nextPageToken")
        if not token:
            break


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "listar":
        listar()
    elif len(sys.argv) == 3 and sys.argv[1] == "subir":
        subir(sys.argv[2])
    else:
        sys.exit(__doc__)
