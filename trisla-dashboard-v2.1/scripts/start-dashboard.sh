#!/bin/bash
set -e
export PATH="$HOME/.local/bin:$PATH"; hash -r
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACK_DIR="$ROOT/backend"
FRONT_DIR="$ROOT/frontend"
echo "🚀 TriSLA Dashboard v2.1 (backend + frontend)"
echo "📦 Raiz: $ROOT"
for p in 5000 5173; do
  if lsof -i:$p >/dev/null 2>&1; then echo "⚠️  Porta $p está em uso. Encerrando..."; fuser -k ${p}/tcp || true; sleep 1; fi
done
cd "$BACK_DIR"; python3 -m pip install --user --upgrade pip >/dev/null; pip3 install --user -r requirements.txt >/dev/null
uvicorn main:app --host 0.0.0.0 --port 5000 >"$ROOT/backend.log" 2>&1 & BACK_PID=$!; sleep 2; echo "✅ Backend PID: $BACK_PID"
cd "$FRONT_DIR"; npm install >/dev/null; npm run dev >/dev/null & FRONT_PID=$!; sleep 4; echo "✅ Frontend PID: $FRONT_PID"
echo "🔗 UI: http://localhost:5173 | API: http://localhost:5000"
trap "echo '🛑 Encerrando...'; kill $BACK_PID $FRONT_PID >/dev/null 2>&1; echo '✅ Encerrado.'" EXIT
wait
