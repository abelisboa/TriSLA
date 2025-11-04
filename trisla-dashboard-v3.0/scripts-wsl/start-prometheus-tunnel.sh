#!/usr/bin/env bash
set -euo pipefail
if lsof -i :9090 >/dev/null 2>&1; then fuser -k 9090/tcp || true; sleep 1; fi
ssh -N -L 9090:localhost:9090 -J porvir5g@ppgca.unisinos.br porvir5g@node006 &
PID=$!; sleep 2
if curl -fsS http://localhost:9090/-/ready >/dev/null 2>&1; then
  echo "🟢 Prometheus conectado (PID $PID)."
else
  echo "🔴 Falha ao conectar Prometheus."; kill -9 "$PID" >/dev/null 2>&1 || true; exit 1
fi
