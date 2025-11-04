#!/usr/bin/env bash
set -eo pipefail
JUMP_HOST="ppgca.unisinos.br"
NASP_HOST="node1"

echo "======================================================"
echo "🚇  Conector TriSLA ↔ NASP v3.2.3"
echo "======================================================"

if ssh -q -o BatchMode=yes "$JUMP_HOST" exit; then
  echo "✅ SSH jump host ok."
else
  echo "❌ SSH indisponível"; exit 1
fi

ssh -f -N -J "$JUMP_HOST" "$NASP_HOST" -L 9092:127.0.0.1:9090 || true
ssh -f -N -J "$JUMP_HOST" "$NASP_HOST" -L 8090:127.0.0.1:8080 || true

sleep 2
PROM_READY=$(curl -fs "http://localhost:9092/-/ready" || echo "fail")
SEM_READY=$(curl -fs "http://localhost:8090/api/v1/health" || echo "fail")

[[ $PROM_READY != fail ]] && echo "🟢 Prometheus online" || echo "🔴 Prometheus offline"
[[ $SEM_READY != fail ]] && echo "🟢 SEM-NSMF online" || echo "🔴 SEM-NSMF offline"

echo "✅ Conexões configuradas."
