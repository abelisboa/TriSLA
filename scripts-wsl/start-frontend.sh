#!/bin/bash
# Script para iniciar apenas o frontend
# Uso: ./scripts-wsl/start-frontend.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🎨 Iniciando frontend..."
cd "$PROJECT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    echo "   ⚠️  node_modules não encontrado. Instalando dependências..."
    npm install
fi

echo "   Iniciando Vite..."
npm run dev





