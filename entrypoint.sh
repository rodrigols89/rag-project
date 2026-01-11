#!/bin/bash

set -e

# Cria diretórios necessários se não existirem
mkdir -p /code/static /code/media /code/staticfiles

# Ajusta permissões e ownership dos diretórios
# Garante que o usuário appuser (UID 1000) possa escrever neles
chmod -R 755 /code/static /code/media /code/staticfiles

# Descobre o UID/GID do "appuser" que FOI CRIADO no Dockerfile
APPUSER_UID=$(id -u appuser 2>/dev/null || echo "1000")
APPUSER_GID=$(id -g appuser 2>/dev/null || echo "1000")

if [ "$(id -u)" = "0" ]; then
    chown -R ${APPUSER_UID}:${APPUSER_GID} \
        /code/static /code/media /code/staticfiles 2>/dev/null || true
    exec gosu appuser "$@"
else
    # Se já estiver rodando como "appuser", apenas executa
    exec "$@"
fi
