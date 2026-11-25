# Tarea en la nube: 1 vídeo LARGO horizontal (16:9)

Sirve para los dos canales. El prompt de la rutina te dice cuál te toca:

| Canal | `--canal` | Carpeta de episodios | Variables | Voz | Tema |
|---|---|---|---|---|---|
| Archivos Malditos TV | *(nada)* | `episodios/` | `YT_*` | es-ES-AlvaroNeural | historia oscura, misterios y curiosidades históricas reales |
| Escribas del Tiempo | `civ` | `episodios_civ/` | `YT_CIV_*` | es-ES-ElviraNeural | civilizaciones antiguas |

No toques nunca la carpeta ni las variables del otro canal.

1. **Preparación.** Ejecuta `pip install -r requirements.txt` y comprueba que existen las 3 variables del canal, sin imprimir sus valores. Si falta alguna, para y avísalo. Si las conexiones HTTPS fallan por certificados, exporta `SSL_CERT_FILE` y `REQUESTS_CA_BUNDLE` con el CA bundle del proxy que indique el entorno.
2. **Qué hay ya.** Ejecuta `python youtube_api.py [--canal civ] listar` y lee la carpeta de episodios del canal. No repitas ningún tema ya publicado, ni en Short ni en vídeo largo.
3. **Tema.** Usa WebSearch para ver qué vídeos largos del nicho funcionan ahora. Elige un tema real con más recorrido que un Short: una historia completa con contexto, desarrollo y desenlace. Contrasta los datos con al menos 2 fuentes fiables y marca lo dudoso como dudoso. Nada de pseudohistoria presentada como hecho.
4. **Guion.**
   - De 3 a 5 minutos: 14-20 segmentos de 2-3 frases cada uno, unas 450-650 palabras en total.
   - Estructura: gancho fuerte en los primeros 10 segundos, contexto, desarrollo con giros, desenlace y cierre que pida suscribirse.
   - Cada segmento lleva su `image`: un prompt en inglés de escena amplia y cinematográfica, sin texto, sin gore y sin personas reales vivas.
5. **Episodio.** Guárdalo en `<carpeta>/AAAA-MM-DD-largo-slug.json`. Copia `voice` y `style` del último episodio del canal (quitando "vertical composition" si aparece) y añade:
   - `"formato": "horizontal"`.
   - `"thumb_text"`: 3-6 palabras impactantes para la miniatura.
   - `title`: SIN #shorts, gancho claro, menos de 70 caracteres.
   - `description`: 3-4 frases que resuman el vídeo, una línea para suscribirse al canal (con su nombre) y 4-6 hashtags.
   - `tags`: 10-15.
6. **Montaje.** Ejecuta `python make_short.py <carpeta>/<archivo>.json` en segundo plano. Las imágenes gratuitas tardan, así que puede llevar más de una hora. Si falla por una imagen, espera un minuto y relánzalo: las imágenes ya descargadas se reutilizan. Hasta 4 intentos.
7. **Revisión.** Extrae 3 fotogramas de `video.mp4` con ffmpeg, abre `miniatura.jpg` y míralos. Comprueba que los subtítulos se leen y que la miniatura tiene texto legible.
8. **Subida.** Ejecuta `python youtube_api.py [--canal civ] subir salida/<slug>`. Sube `video.mp4` e intenta poner la miniatura.
9. **Registro.** Haz commit del JSON y push a main. Si no se permite, no pasa nada.
10. **Informe.** En 3 líneas: tema, enlace, visibilidad y si se puso la miniatura.
