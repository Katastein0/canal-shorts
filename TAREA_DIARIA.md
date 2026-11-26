# Tarea diaria: un Short nuevo de "Historia oscura" (español)

> **Antes de escribir el guion, lee y cumple `GUIA_CONTENIDO.md`** (gancho, `hook_text`, pregunta final, título y `playlist`).

Nicho del canal: historia oscura, misterios y curiosidades históricas reales. Shorts verticales de 40-55 s, voz en español de España (es-ES-AlvaroNeural).

## Pasos
1. **Tendencias.** En YouTube (navegador), busca Shorts recientes del nicho: "historia oscura", "misterios de la historia", "sabías que historia", "dark history shorts". Apunta 5-10 vídeos con muchas visitas recientes y fíjate en el tema, el gancho y el título. Si usas WebSearch, busca también efemérides del día.
2. **Tema.** Elige un hecho histórico real y verificable que no esté ya en `episodios/` (no repitas temas; esta tarea corre 5 veces al día, así que revisa también los episodios de hoy y varía época y región). Contrasta los datos con al menos una fuente fiable. Si un dato está en duda, dilo como tal ("según algunas crónicas…").
3. **Guion.** 6-8 segmentos de 1-2 frases (unas 110-140 palabras en total). El primer segmento es un gancho fuerte en menos de 3 s, el último pide un comentario o el follow. Cada segmento lleva `image`: un prompt en inglés que describa la escena (el estilo se añade solo). Sin personas reales reconocibles ni gore explícito.
4. **Episodio.** Guarda `episodios/AAAA-MM-DD-slug.json` con el mismo formato que los anteriores (slug, title con emoji + #shorts, description con hashtags, tags, segments). El canal se llama **Archivos Malditos TV** (@ArchivosMalditosTV): la description termina siempre con "Suscríbete a Archivos Malditos TV para más historia oscura cada día." y entre sus hashtags va `#ArchivosMalditos`; añade también "archivos malditos" a los tags.
5. **Montaje.** Ejecuta `python make_short.py episodios/AAAA-MM-DD-slug.json` (tarda unos 10 min; las imágenes vienen de un servicio gratuito que a veces va lento). Si falla una imagen, vuelve a ejecutarlo: las imágenes ya descargadas se reutilizan.
6. **Revisión.** Extrae 2-3 fotogramas con ffmpeg y míralos: subtítulos legibles, sin texto raro en las imágenes. Comprueba que el vídeo dura menos de 60 s.
7. **Entrega.** Deja en `salida/<slug>/` los archivos `short.mp4`, `short_subida.mp4` (copia <10 MB para subir desde el navegador), `metadata.txt` y `guion.txt`. Borra `_tmp/`. No lo subas a YouTube salvo que el dueño del canal lo pida en esa conversación.

Requisitos (una vez): `python -m pip install imageio-ffmpeg pillow edge-tts`
