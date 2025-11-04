#!/bin/bash
# Script auxiliar para abrir navegador no WSL
# Uso: ./scripts-wsl/open-browser.sh [URL]

URL=${1:-"http://localhost:5000"}

if command -v wslview > /dev/null; then
    wslview "$URL" 2>/dev/null &
elif command -v cmd.exe > /dev/null; then
    cmd.exe /c start "$URL" 2>/dev/null &
elif command -v xdg-open > /dev/null; then
    xdg-open "$URL" 2>/dev/null &
else
    echo "⚠️  Não foi possível abrir o navegador automaticamente"
    echo "   Abra manualmente: $URL"
    exit 1
fi

echo "✅ Navegador aberto em $URL"





