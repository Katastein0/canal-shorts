"""Sube Shorts y lista los vídeos de un canal con la API de YouTube.

Credenciales por variables de entorno (nunca en el repo):
  canal por defecto (historia oscura):   YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
  con --canal civ (civilizaciones):      YT_CIV_CLIENT_ID, YT_CIV_CLIENT_SECRET, YT_CIV_REFRESH_TOKEN

Uso:
  python youtube_api.py [--canal civ] subir salida/<slug>   # sube short.mp4 o video.mp4 (+miniatura.jpg) con la metadata del episodio
  python youtube_api.py [--canal civ] listar                # títulos ya publicados (para no repetir temas)
  python youtube_api.py [--canal civ] ranking               # vídeos ordenados por visitas y me gusta

El JSON del episodio se busca como <slug>.json en episodios/ o episodios_*/.
"""
import json, os, sys, time
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
                        token_uri="https://oauth2.googleapis.com/token")
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
    largo = (carpeta / "video.mp4").exists()
    archivo = carpeta / ("video.mp4" if largo else "short.mp4")
    media = MediaFileUpload(str(archivo), mimetype="video/mp4", resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    vid = resp["id"]
    estado = yt.videos().list(part="status", id=vid).execute()["items"][0]["status"]["privacyStatus"]
    enlace = f"https://youtube.com/watch?v={vid}" if largo else f"https://youtube.com/shorts/{vid}"
    print(f"SUBIDO {enlace}  visibilidad={estado}")
    mini = carpeta / "miniatura.jpg"
    if largo and mini.exists():
        try:
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(mini), mimetype="image/jpeg")).execute()
            print("Miniatura puesta.")
        except Exception as e:
            print(f"AVISO: no se pudo poner la miniatura (¿canal sin verificar por teléfono?): {str(e)[:200]}")
    if ep.get("playlist"):
        a_lista(yt, vid, ep["playlist"])
    if estado != "public":
        print("AVISO: YouTube lo ha dejado en privado (proyecto de API sin auditar). Hay que hacerlo público a mano en Studio.")


def a_lista(yt, vid, nombre):
    """Añade el vídeo a la lista temática `nombre`, creándola si no existe.
    Necesita el permiso completo de YouTube (obtener_token.py lo pide desde ahora)."""
    try:
        listas, token = [], None
        while True:
            r = yt.playlists().list(part="snippet", mine=True, maxResults=50, pageToken=token).execute()
            listas += r["items"]
            token = r.get("nextPageToken")
            if not token:
                break
        lid = next((l["id"] for l in listas if l["snippet"]["title"].strip().lower() == nombre.strip().lower()), None)
        if not lid:
            lid = yt.playlists().insert(part="snippet,status", body={
                "snippet": {"title": nombre, "defaultLanguage": "es"},
                "status": {"privacyStatus": "public"}}).execute()["id"]
            print(f"Lista creada: {nombre}")
        # YouTube devuelve a veces 409/5xx justo después de subir el vídeo o crear la lista:
        # reintentamos con espera creciente.
        for intento in range(6):
            try:
                yt.playlistItems().insert(part="snippet", body={"snippet": {
                    "playlistId": lid, "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
                print(f"Añadido a la lista: {nombre}")
                return
            except Exception as e:
                codigo = getattr(getattr(e, "resp", None), "status", None)
                if codigo not in (409, 500, 503) or intento == 5:
                    raise
                time.sleep(20 * (intento + 1))
    except Exception as e:
        print(f"AVISO: no se pudo añadir a la lista '{nombre}' : {str(e)[:160]}")


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


def ranking(prefijo):
    """Vídeos del canal ordenados por visualizaciones, con me gusta y tipo (Short o largo).
    Sirve para copiar lo que funciona: temas, títulos y ganchos de los de arriba."""
    yt = client(prefijo)
    ch = yt.channels().list(part="snippet,contentDetails,statistics", mine=True).execute()["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, token = [], None
    while True:
        r = yt.playlistItems().list(part="contentDetails", playlistId=uploads, maxResults=50, pageToken=token).execute()
        ids += [it["contentDetails"]["videoId"] for it in r["items"]]
        token = r.get("nextPageToken")
        if not token:
            break
    filas = []
    for i in range(0, len(ids), 50):
        r = yt.videos().list(part="snippet,statistics", id=",".join(ids[i:i + 50])).execute()
        for v in r["items"]:
            tipo = "SHORT" if "#shorts" in v["snippet"]["title"].lower() else "LARGO"
            st = v["statistics"]
            filas.append((int(st.get("viewCount", 0)), int(st.get("likeCount", 0)), tipo,
                          v["snippet"]["publishedAt"][:10], v["snippet"]["title"]))
    filas.sort(reverse=True)
    print(f"# Canal: {ch['snippet']['title']} | suscriptores: {ch['statistics'].get('subscriberCount')}")
    print("visitas | me gusta | tipo | fecha | título")
    for vis, lk, tipo, fecha, titulo in filas:
        print(f"{vis:>7} | {lk:>4} | {tipo:<5} | {fecha} | {titulo}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    prefijo = "YT_"
    if len(args) >= 2 and args[0] == "--canal":
        prefijo = f"YT_{args[1].upper()}_"
        args = args[2:]
    if args[:1] == ["listar"]:
        listar(prefijo)
    elif args[:1] == ["ranking"]:
        ranking(prefijo)
    elif len(args) == 2 and args[0] == "subir":
        subir(prefijo, args[1])
    else:
        sys.exit(__doc__)
