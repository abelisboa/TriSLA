#!/usr/bin/env bash
# PROMPT_230 — campanha de contraste (port-forwards + Python). Executar na raiz do repositório.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT" || exit 1
[ -f /tmp/kubeconfig.node2 ] && export KUBECONFIG=/tmp/kubeconfig.node2

export TRISLA_PROMETHEUS_QUERY_URL="${TRISLA_PROMETHEUS_QUERY_URL:-http://127.0.0.1:19090/api/v1/query}"
export TRISLA_BACKEND_URL="${TRISLA_BACKEND_URL:-http://127.0.0.1:18001}"
export ONOS_USER="${ONOS_USER:-onos}"
export ONOS_PASSWORD="${ONOS_PASSWORD:-rocks}"
export TRISLA_FASE2_IPERF_SERVER="${TRISLA_FASE2_IPERF_SERVER:-192.168.100.51}"

PF_PIDS=()
cleanup() {
  for pid in "${PF_PIDS[@]:-}"; do
    kill "$pid" >/dev/null 2>&1 || true
  done
}
trap cleanup EXIT

kubectl -n monitoring port-forward svc/prometheus-kube-prometheus-prometheus 19090:9090 >/tmp/p230_pf_prom.log 2>&1 &
PF_PIDS+=($!)

kubectl -n trisla port-forward svc/trisla-portal-backend 18001:8001 >/tmp/p230_pf_backend.log 2>&1 &
PF_PIDS+=($!)

kubectl -n nasp-transport port-forward svc/onos 18181:8181 >/tmp/p230_pf_onos.log 2>&1 &
PF_PIDS+=($!)

kubectl -n trisla port-forward svc/trisla-besu 18545:8545 >/tmp/p230_pf_besu.log 2>&1 &
PF_PIDS+=($!)

sleep 6

export TRISLA_ONOS_BASE="${TRISLA_ONOS_BASE:-http://127.0.0.1:18181/onos/v1}"
export TRISLA_BC_RPC_URL="${TRISLA_BC_RPC_URL:-http://127.0.0.1:18545}"

echo "[INFO] Iniciando campanha complementar de contraste"
python3 docs/scripts/prompt230_contrast_campaign.py
echo "[INFO] Campanha concluída"
