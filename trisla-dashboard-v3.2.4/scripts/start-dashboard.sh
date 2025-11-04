#!/usr/bin/env bash
set -e
echo "🚀 Iniciando TriSLA Dashboard..."
(cd backend && nohup python3 main.py > ../backend.log 2>&1 &)
(cd frontend && nohup npm run dev -- --port=5174 > ../frontend.log 2>&1 &)
echo "✅ Backend e frontend iniciados."
