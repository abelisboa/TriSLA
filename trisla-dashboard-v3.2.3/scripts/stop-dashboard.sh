#!/usr/bin/env bash
pkill -f 'python3 main.py' || true
pkill -f 'vite' || true
echo "✅ Tudo encerrado."
