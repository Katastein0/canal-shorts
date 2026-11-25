"""Sube Shorts y lista los vídeos de un canal con la API de YouTube.

Credenciales por variables de entorno (nunca en el repo):
  canal por defecto (historia oscura):   YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
  con --canal civ (civilizaciones):      YT_CIV_CLIENT_ID, YT_CIV_CLIENT_SECRET, YT_CIV_REFRESH_TOKEN

Uso:
  python youtube_api.py [--canal civ] subir salida/<slug>   # sube short.mp4 con la metadata del episodio
  python youtube_api.py [--canal civ] listar                # títulos ya publicados (para no repetir temas)

El JSON del episodio se busca como <slug>.json en episodios/ o episodios_*/.
"""
import json, os, sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.readonly"]
RAIZ = Path(__file__).parent


def client(prefijo):
    nombres = [f"{prefijo}{n}" for n in ("CLIENT_ID", "CLIENT_SECRET", "REFRESH_TOKEN")]
    faltan = [v for v in nombres if not os.environ.get(v)]
    if faltan:
        sys.exit(f"Faltan variables de entorno: {', '.join(faltan)}")
    cid, secret, refresh = (os.environ[v] for v in nombres)
    creds = Credentials(None, refresh_token=refresh, client_id=cid, client_secret=secret,
                        token_uri="https://oauth2.googleapis.com/token", scopes=SCOPES)
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def buscar_episodio(slug):
    for d in [RAIZ / "episodios", *sorted(RAIZ.glob("episodios_*"))]:
        p = d / f"{slug}.json"
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    sys.exit(f"No encuentro el episodio {slug}.json en episodios/ ni episodios_*/")


def subir(prefijo, carpeta):
    carpeta = Path(carpeta)
    ep = buscar_episodio(carpeta.name)
    body = {
        "snippet": {"title": ep["title"][:100], "description": ep["description"],
                    "tags": ep["tags"], "categoryId": "27", "defaultLanguage": "es",
                    "defaultAudioLanguage": "es"},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False,
                   "containsSyntheticMedia": True},
    }
    yt = client(prefijo)
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


def listar(prefijo):
    yt = client(prefijo)
    ch = yt.channels().list(part="snippet,contentDetails", mine=True).execute()["items"][0]
    print(f"# Canal: {ch['snippet']['title']}")
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
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    prefijo = "YT_"
    if len(args) >= 2 and args[0] == "--canal":
        prefijo = f"YT_{args[1].upper()}_"
        args = args[2:]
    if args[:1] == ["listar"]:
        listar(prefijo)
    elif len(args) == 2 and args[0] == "subir":
        subir(prefijo, args[1])
    else:
        sys.exit(__doc__)
