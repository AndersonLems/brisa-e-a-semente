#!/usr/bin/env bash
# Lançador: instala o pygame-ce se faltar e abre o jogo.
cd "$(dirname "$0")" || exit 1
if ! python3 -c "import pygame" 2>/dev/null; then
    echo "Instalando pygame-ce..."
    pip3 install --user --break-system-packages pygame-ce || exit 1
fi
exec python3 main.py "$@"
