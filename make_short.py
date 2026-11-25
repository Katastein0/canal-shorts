"""Monta un vídeo a partir de un episodio JSON: Short vertical (1080x1920) o vídeo horizontal (1920x1080).

Uso:  python make_short.py episodios/2026-11-25-slug.json

El JSON tiene: slug, title, description, tags, segments y, opcionales:
  formato  "vertical" (por defecto, Short) u "horizontal" (vídeo largo 16:9)
  voice, rate, style   (voz edge-tts, velocidad, estilo de imagen)
  thumb_text           texto grande de la miniatura (solo horizontal)
"segments": [{"text": "...narración...", "image": "prompt en inglés"}, ...]

Salida en salida/<slug>/:
  vertical:   short.mp4, short_subida.mp4 (<10 MB), metadata.txt, guion.txt
  horizontal: video.mp4, miniatura.jpg, metadata.txt, guion.txt
Voz: edge-tts (voces neurales de Microsoft, gratis). Imágenes: pollinations.ai (gratis).
"""
import asyncio, json, os, re, subprocess, sys, time, urllib.parse, urllib.request
from pathlib import Path

import edge_tts
import edge_tts.communicate
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
# En la nube el tráfico pasa por un proxy con su propio certificado: edge-tts no lo
# lee por sí solo, así que le pasamos el proxy y el CA indicado en SSL_CERT_FILE.
PROXY = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
if os.environ.get("SSL_CERT_FILE") and os.path.exists(os.environ["SSL_CERT_FILE"]):
    import ssl
    edge_tts.communicate._SSL_CTX = ssl.create_default_context(cafile=os.environ["SSL_CERT_FILE"])
FPS = 30
FUENTES = [r"C:\Windows\Fonts\impact.ttf", r"C:\Windows\Fonts\arialbd.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
           "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
           "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"]
FONT = next((f for f in FUENTES if os.path.exists(f)), None)
STYLE = ", dark cinematic oil painting, dramatic chiaroscuro lighting, highly detailed, no text"

FORMATOS = {
    # ancho, alto, tamaño máx. subtítulo, alto franja subtítulo, posición y de la franja
    "vertical":   dict(W=1080, H=1920, cap=92, cap_h=400, cap_y=1920 - 820, comp="vertical composition"),
    "horizontal": dict(W=1920, H=1080, cap=64, cap_h=260, cap_y=1080 - 300, comp="wide cinematic composition"),
}


def fuente(size):
    if FONT:
        return ImageFont.truetype(FONT, size)
    try:
        return ImageFont.load_default(size=size)  # Pillow >= 10.1
    except TypeError:
        return ImageFont.load_default()


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError(p.stderr[-2000:])
    return p


def duration(path):
    p = subprocess.run([FFMPEG, "-i", str(path)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", p.stderr).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


async def tts(text, voice, rate, out):
    com = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary", proxy=PROXY)
    words = []
    with open(out, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append((ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7, ch["text"]))
    return words


def fetch_image(prompt, seed, out, style, F):
    url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(f"{prompt}{style}, {F['comp']}")
           + f"?width={F['W']}&height={F['H']}&nologo=true&seed={seed}")
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "shorts-pipeline"})
            data = urllib.request.urlopen(req, timeout=180).read()
            if data[:3] == b"\xff\xd8\xff" or data[:4] == b"\x89PNG":
                out.write_bytes(data)
                Image.open(out).verify()
                return
        except Exception as e:
            print(f"  imagen reintento {attempt + 1}: {e}", flush=True)
        time.sleep(15 * (attempt + 1))
    raise RuntimeError(f"No se pudo generar la imagen: {prompt}")


def caption_png(text, out, F):
    W = F["W"]
    img = Image.new("RGBA", (W, F["cap_h"]), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    size = F["cap"]
    font = fuente(size)
    while d.textlength(text, font=font) > W - 120 and size > 36:
        size -= 6
        font = fuente(size)
    tw = d.textlength(text, font=font)
    d.text(((W - tw) / 2, F["cap_h"] * 0.35), text, font=font, fill=(255, 230, 60),
           stroke_width=max(4, size // 11), stroke_fill=(0, 0, 0))
    img.save(out)


def chunk_words(words, n):
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == n or re.search(r"[.,;:?!]$", w[2]):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return [(c[0][0], c[-1][1], " ".join(x[2] for x in c).upper()) for c in chunks]


def build_segment(i, img, audio, words, tmp, F):
    W, H = F["W"], F["H"]
    dur = duration(audio) + 0.25
    frames = int(dur * FPS) + 1
    zoom = "min(zoom+0.0009,1.18)" if i % 2 == 0 else "if(eq(on,0),1.18,max(zoom-0.0009,1.0))"
    caps = chunk_words(words, 3 if H > W else 5)
    inputs = ["-loop", "1", "-i", str(img), "-i", str(audio)]
    for j, (a, b, t) in enumerate(caps):
        p = tmp / f"cap_{i}_{j}.png"
        caption_png(t, p, F)
        inputs += ["-i", str(p)]
    # recorta la marca de agua inferior, rellena el formato y aplica Ken Burns
    fg = (f"[0:v]crop=iw:ih*0.93:0:0,scale={W*2}:{H*2}:force_original_aspect_ratio=increase,"
          f"crop={W*2}:{H*2},zoompan=z='{zoom}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},"
          f"eq=contrast=1.05:saturation=1.1,vignette=PI/5[v0]")
    last = "v0"
    for j, (a, b, _) in enumerate(caps):
        fg += f";[{last}][{j+2}:v]overlay=0:{F['cap_y']}:enable='between(t,{a:.2f},{b+0.05:.2f})'[v{j+1}]"
        last = f"v{j+1}"
    out = tmp / f"seg_{i:02d}.mp4"
    run([FFMPEG, "-y", *inputs, "-filter_complex", fg, "-map", f"[{last}]", "-map", "1:a",
         "-t", f"{dur:.2f}", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-af", "apad", str(out)])
    return out


def miniatura(img_path, texto, out):
    """Miniatura 1280x720: imagen de fondo oscurecida y texto grande a la izquierda."""
    W, H = 1280, 720
    im = Image.open(img_path).convert("RGB")
    im = im.crop((0, 0, im.width, int(im.height * 0.93)))
    r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1))
    im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sombra)
    for x in range(W):
        ds.line([(x, 0), (x, H)], fill=(0, 0, 0, int(200 * max(0, 1 - x / (W * 0.75)))))
    im = Image.alpha_composite(im.convert("RGBA"), sombra)
    d = ImageDraw.Draw(im)
    palabras, lineas, size = texto.upper().split(), [], 120
    while True:
        font = fuente(size)
        lineas, cur = [], ""
        for p in palabras:
            prueba = f"{cur} {p}".strip()
            if d.textlength(prueba, font=font) <= W * 0.62:
                cur = prueba
            else:
                lineas.append(cur)
                cur = p
        lineas.append(cur)
        if len(lineas) <= 3 or size <= 60:
            break
        size -= 10
    y = (H - len(lineas) * size * 1.1) / 2
    for i, l in enumerate(lineas):
        color = (255, 230, 60) if i == 0 else (255, 255, 255)
        d.text((60, y + i * size * 1.1), l, font=font, fill=color, stroke_width=max(4, size // 12), stroke_fill=(0, 0, 0))
    im.convert("RGB").save(out, quality=90)


def main(ep_path):
    ep = json.loads(Path(ep_path).read_text(encoding="utf-8"))
    formato = ep.get("formato", "vertical")
    F = FORMATOS[formato]
    base = Path(__file__).resolve().parent / "salida" / ep["slug"]
    tmp = base / "_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    voice, rate = ep.get("voice", "es-ES-AlvaroNeural"), ep.get("rate", "+8%")
    style = ep.get("style", STYLE).replace(", vertical composition", "")
    segs = []
    for i, s in enumerate(ep["segments"]):
        print(f"[{i+1}/{len(ep['segments'])}] voz + imagen", flush=True)
        audio = tmp / f"voz_{i:02d}.mp3"
        words = asyncio.run(tts(s["text"], voice, rate, audio))
        img = tmp / f"img_{i:02d}.jpg"
        if not img.exists():
            fetch_image(s["image"], 1000 + i, img, style, F)
        segs.append(build_segment(i, img, audio, words, tmp, F))
    lst = tmp / "lista.txt"
    lst.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in segs), encoding="utf-8")
    final = base / ("short.mp4" if formato == "vertical" else "video.mp4")
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", "-movflags", "+faststart", str(final)])
    (base / "guion.txt").write_text("\n\n".join(s["text"] for s in ep["segments"]), encoding="utf-8")
    (base / "metadata.txt").write_text(
        f"TÍTULO:\n{ep['title']}\n\nDESCRIPCIÓN:\n{ep['description']}\n\nETIQUETAS:\n{', '.join(ep['tags'])}\n",
        encoding="utf-8")
    d = duration(final)
    if formato == "vertical":
        # copia ligera (<10 MB) para subir desde el navegador; YouTube recomprime igualmente
        run([FFMPEG, "-y", "-i", str(final), "-c:v", "libx264", "-preset", "slow", "-b:v", "1100k",
             "-maxrate", "1300k", "-bufsize", "2600k", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart",
             str(base / "short_subida.mp4")])
        if d > 60:
            print("AVISO: dura más de 60 s; YouTube lo acepta como Short hasta 3 min, pero <60 s rinde mejor.")
    else:
        miniatura(tmp / "img_00.jpg", ep.get("thumb_text", ep["title"]), base / "miniatura.jpg")
    print(f"OK -> {final}  ({d:.1f} s)")


if __name__ == "__main__":
    main(sys.argv[1])
