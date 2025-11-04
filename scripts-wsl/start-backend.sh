#!/bin/bash
# Script para iniciar apenas o backend
# Uso: ./scripts-wsl/start-backend.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔧 Iniciando backend..."
cd "$PROJECT_DIR/backend"

if [ -d "venv" ]; then
    echo "   Ativando venv..."
    source venv/bin/activate
else
    echo "   ⚠️  venv não encontrado. Execute: ./scripts-wsl/install-dependencies.sh"
    exit 1
fi

echo "   Iniciando uvicorn..."
python -m uvicorn main:app --reload --port 5000





