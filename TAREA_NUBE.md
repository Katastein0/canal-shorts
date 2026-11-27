# Tarea en la nube: crear y subir 1 Short de "Historia oscura"

> **Antes de elegir tema, ejecuta `python youtube_api.py [--canal civ] ranking` y lee y cumple `GUIA_CONTENIDO.md`**: el vídeo nuevo debe imitar el tipo de tema, el título y el gancho de los 3 Shorts con más visitas del canal. Cumple también el gancho, `hook_text`, pregunta final y `playlist`.

Esta tarea se ejecuta en un agente en la nube, 2 veces al día (además hay 1 vídeo largo diario, ver TAREA_LARGO.md). En cada ejecución se crea y se sube UN Short. Si las conexiones HTTPS fallan por certificados, exporta SSL_CERT_FILE y REQUESTS_CA_BUNDLE con el CA bundle del proxy que indique el entorno.

1. **Preparación.** Ejecuta `source preparar_nube.sh` (en el mismo comando que los siguientes, o vuelve a hacer `export` de SSL_CERT_FILE y REQUESTS_CA_BUNDLE en cada comando) y usa siempre `python`. Comprueba que existen YT_CLIENT_ID, YT_CLIENT_SECRET y YT_REFRESH_TOKEN, sin imprimir sus valores. Si falta alguna, para y avísalo.
2. **Qué hay ya.** Ejecuta `python youtube_api.py listar` y lee los JSON de `episodios/`. No repitas ningún tema ya publicado y varía la época y la región respecto a los últimos vídeos.
3. **Tendencias y tema.** Usa WebSearch para buscar qué Shorts de historia oscura, misterios históricos o curiosidades funcionan ahora, y efemérides del día. Elige un hecho histórico real y verificable, y contrasta los datos con al menos una fuente fiable. Si un dato está en duda, dilo como tal ("según algunas crónicas…").
4. **Guion y episodio.** Sigue los pasos 3 y 4 de `TAREA_DIARIA.md` (formato JSON, gancho inicial, 110-140 palabras, prompts de imagen en inglés, nada de gore ni personas reales reconocibles). Guárdalo en `episodios/AAAA-MM-DD-slug.json`.
5. **Montaje.** Ejecuta `python make_short.py episodios/<archivo>.json`. Si falla por las imágenes, espera un minuto y vuelve a ejecutarlo; hasta 3 intentos.
6. **Revisión.** Extrae 2 fotogramas con ffmpeg (la ruta sale de `python -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"`) y míralos. Comprueba que dura menos de 60 s.
7. **Subida.** Ejecuta `python youtube_api.py subir salida/<slug>`.
8. **Registro.** Haz commit del JSON del episodio y push a la rama principal. Si el push a main no está permitido, déjalo en la rama que te dejen: el paso 2 ya evita repetir temas usando la lista del canal.
9. **Informe.** En 3 líneas: tema, enlace del Short y visibilidad (público o privado). Si algo falló, explica qué.
