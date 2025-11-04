#!/usr/bin/env bash
set -euo pipefail
echo "🛑 Encerrando TriSLA Dashboard e túneis"
pkill -f "uvicorn backend.main:app" || true
pkill -f "vite" || true
for p in 9090 9091 9092 8080 8088 8090; do fuser -k ${p}/tcp >/dev/null 2>&1 || true; done
if ssh -o BatchMode=yes -J ppgca.unisinos.br node1 "true" >/dev/null 2>&1; then
  ssh -J ppgca.unisinos.br node1 "pgrep -a kubectl | grep 'port-forward' | awk '{print \$1}' | xargs -r kill -9 || true"
fi
echo "✅ Tudo encerrado."
