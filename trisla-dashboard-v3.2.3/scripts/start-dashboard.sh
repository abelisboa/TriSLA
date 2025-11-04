#!/usr/bin/env bash
set -eo pipefail
echo "🚀 Iniciando TriSLA Dashboard..."
cd "$(dirname "$0")/.."
cd backend && nohup python3 main.py > ../backend.log 2>&1 &
cd ../frontend && nohup npx vite --port=5174 > ../frontend.log 2>&1 &
echo "✅ Backend e frontend iniciados."
