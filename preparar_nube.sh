#!/usr/bin/env bash
# Prepara el entorno de la nube: ejecuta `source preparar_nube.sh` al empezar.
# Instala las dependencias en el MISMO Python que ejecuta los scripts y configura
# los certificados del proxy de salida.
PY=python
$PY -m pip install -q --ignore-installed cffi cryptography pillow 2>&1 | grep -v WARNING
$PY -m pip install -q -r requirements.txt 2>&1 | grep -v WARNING
if [ -f /root/.ccr/ca-bundle.crt ]; then
  export SSL_CERT_FILE=/root/.ccr/ca-bundle.crt REQUESTS_CA_BUNDLE=/root/.ccr/ca-bundle.crt
fi
$PY -c "import google.oauth2, PIL.Image, edge_tts, imageio_ffmpeg; print('entorno OK')"
