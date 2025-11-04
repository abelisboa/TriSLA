#!/usr/bin/env bash
echo "🛑 Encerrando TriSLA Dashboard..."
pkill -f "python3 main.py" || true
pkill -f "vite" || true
echo "✅ Tudo encerrado."
