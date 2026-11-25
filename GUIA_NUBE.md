# Pasar el canal a la nube: lo que tienes que hacer tú

Son pasos con tus cuentas y contraseñas, por eso los haces tú. Tardas unos 20 minutos.

## A. GitHub (2 min)
1. Entra en https://github.com/new y crea un repositorio **privado** y vacío llamado `canal-shorts`. No marques README ni .gitignore.
2. Pásame la URL en el chat. Yo subo el proyecto. La primera vez, Windows te pedirá iniciar sesión en GitHub.
3. Si claude.ai te pide dar acceso de la app de Claude a ese repositorio, acéptalo. Sin ese acceso, el agente de la nube no puede leerlo.

## B. Google Cloud: permiso para subir vídeos (10 min)
1. Entra en https://console.cloud.google.com con la cuenta del canal y crea un proyecto nuevo, por ejemplo "Canal Shorts".
2. Ve a **APIs y servicios → Biblioteca**, busca **YouTube Data API v3** y pulsa **Habilitar**.
3. Ve a **Google Auth Platform** (la "pantalla de consentimiento OAuth"):
   - Tipo de usuario: **Externo**. Pon el nombre de la app y tu correo de contacto.
   - En **Público**, pulsa **Publicar app**, para que pase a "En producción". Si se queda en "Prueba", el permiso caduca a los 7 días y la automatización deja de funcionar.
4. Ve a **Clientes → Crear cliente**, elige tipo **Aplicación de escritorio** y descarga el JSON.
5. Guarda ese JSON en `D:\Proyectos\Canal Youtube\Shorts\` con el nombre `client_secret.json`.
6. En PowerShell, dentro de esa carpeta:
   ```
   python obtener_token.py
   ```
   Se abre el navegador. Entra con la cuenta del canal y, si te lo pregunta, elige el canal. Google avisará de que la app no está verificada: pulsa **Configuración avanzada → Ir a … (no seguro)**. Es tu propia app, así que no pasa nada.
7. Se crea el archivo `credenciales_youtube.txt` con 3 líneas.

## C. Entorno de la nube (3 min)
1. En https://claude.ai/code, abre la configuración del entorno **Default**.
2. En **variables de entorno**, pega las 3 líneas de `credenciales_youtube.txt`.
3. En **acceso a red**, permite el acceso completo a internet. El agente necesita llegar a las imágenes (pollinations.ai), a la voz (Microsoft) y a la API de YouTube.
4. Borra `credenciales_youtube.txt` y `client_secret.json` de tu PC. Ya no hacen falta y es mejor que no anden por ahí.

## D. Para que se publiquen como públicos
Google deja en **privado** los vídeos que suben las apps de API sin auditar. Para quitar ese límite:
- Rellena el formulario **"YouTube API Services – Audit and Quota Extension"**: https://support.google.com/youtube/contact/yt_api_form
- Mientras no lo aprueben, cada vídeo llega en privado y tienes que hacerlo público en Studio. Son 2 clics por vídeo.

Cuota: la API da 10.000 unidades al día y cada subida gasta unas 1.600, así que 5 Shorts al día caben justos.
