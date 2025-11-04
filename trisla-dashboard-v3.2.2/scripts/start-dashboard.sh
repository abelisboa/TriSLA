#!/usr/bin/env bash
set -euo pipefail
echo "🚀 Iniciando TriSLA Dashboard (backend + frontend)"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v uvicorn >/dev/null 2>&1; then
  echo "⚠️  uvicorn não encontrado. Instale com: pip install --user -r backend/requirements.txt"
else
  echo "▶️  Subindo backend (uvicorn)..."
  nohup uvicorn backend.main:app --host 0.0.0.0 --port 5000 >/tmp/trisla-backend.log 2>&1 &
  echo "✅ Backend em :5000"
fi

if [ -f "frontend/package.json" ]; then
  if ! command -v vite >/dev/null 2>&1; then
    echo "⚠️  vite não encontrado. Instale com: (cd frontend && npm i)"
  fi
  echo "▶️  Subindo frontend (Vite)..."
  (cd frontend && nohup npm run dev >/tmp/trisla-frontend.log 2>&1 &)
  echo "✅ Frontend (Vite) iniciado"
fi

echo "🔗 UI: http://localhost:5173   |   API: http://localhost:5000"
