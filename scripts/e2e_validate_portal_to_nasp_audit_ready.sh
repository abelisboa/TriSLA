#!/usr/bin/env bash
set -euo pipefail

# ==========================================
# TriSLA — E2E VALIDATION (PRODUCTION GRADE)
# Portal -> NASP Adapter -> CRD -> Namespace -> Quota
# Robust retry, deterministic, audit-ready
# ==========================================

NS="${1:-trisla}"
OUT_BASE="${2:-/home/porvir5g/gtp5g/trisla/evidencias_e2e}"
ADAPTER_SVC="${3:-trisla-nasp-adapter}"
ADAPTER_PORT="${4:-8085}"

TS="$(date -u +%Y%m%dT%H%M%SZ)"
TS_LOWER="$(echo "$TS" | tr '[:upper:]' '[:lower:]')"
EVD="${OUT_BASE}/e2e_validation_${TS}"
mkdir -p "${EVD}"

PF_PID=""

log() { echo -e "$@" | tee -a "${EVD}/run.log"; }

cleanup() {
  if [[ -n "${PF_PID}" ]]; then
    kill "${PF_PID}" >/dev/null 2>&1 || true
    wait "${PF_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "❌ Comando ausente: $1"; exit 1; }
}

require_cmd kubectl
require_cmd python3

log "=================================================="
log "TriSLA — E2E VALIDATION (PRODUCTION GRADE)"
log "Namespace : ${NS}"
log "Service   : ${ADAPTER_SVC}:${ADAPTER_PORT}"
log "Evidence  : ${EVD}"
log "=================================================="

# -------------------------------------------------
# [0] Snapshot do estado atual
# -------------------------------------------------
log "\n[0] Snapshot inicial..."
kubectl get deploy -n "${NS}" trisla-nasp-adapter -o wide | tee "${EVD}/deploy_wide.txt"
kubectl get pods -n "${NS}" | tee "${EVD}/pods.txt"

# -------------------------------------------------
# [1] Port-forward robusto
# -------------------------------------------------
log "\n[1] Iniciando port-forward..."
kubectl -n "${NS}" port-forward "svc/${ADAPTER_SVC}" "${ADAPTER_PORT}:${ADAPTER_PORT}" \
  > "${EVD}/port_forward.log" 2>&1 &
PF_PID="$!"

sleep 2

# Aguarda porta responder
log "[1.1] Aguardando porta local responder..."
for i in {1..15}; do
  if python3 - <<PY >/dev/null 2>&1
import socket
s = socket.socket()
try:
    s.connect(("127.0.0.1", ${ADAPTER_PORT}))
    s.close()
    print("OK")
except:
    raise SystemExit(1)
PY
  then
    log "✅ Porta pronta (tentativa $i)"
    break
  else
    log "⏳ Porta não pronta (tentativa $i)"
    sleep 2
  fi

  if [[ "$i" == "15" ]]; then
    log "❌ Port-forward falhou."
    exit 1
  fi
done

# -------------------------------------------------
# [2] Health check robusto
# -------------------------------------------------
log "\n[2] Health check..."

for i in {1..10}; do
  if python3 - <<PY > "${EVD}/health.json" 2>/dev/null
import urllib.request
with urllib.request.urlopen("http://127.0.0.1:${ADAPTER_PORT}/health", timeout=5) as r:
    print(r.read().decode("utf-8"))
PY
  then
    log "✅ Health OK (tentativa $i)"
    cat "${EVD}/health.json" | tee -a "${EVD}/run.log" >/dev/null
    break
  else
    log "⏳ Health falhou (tentativa $i)"
    sleep 2
  fi

  if [[ "$i" == "10" ]]; then
    log "❌ Health falhou após 10 tentativas."
    exit 1
  fi
done

# -------------------------------------------------
# Helper HTTP POST
# -------------------------------------------------
post_json() {
  local payload="$1"
  local outfile="$2"

  python3 - <<PY > "${outfile}"
import json, urllib.request
payload = json.loads('''${payload}''')
req = urllib.request.Request(
    "http://127.0.0.1:${ADAPTER_PORT}/api/v1/nsi/instantiate",
    data=json.dumps(payload).encode(),
    headers={"Content-Type":"application/json"},
    method="POST"
)
with urllib.request.urlopen(req, timeout=15) as r:
    print(r.read().decode())
PY
}

# -------------------------------------------------
# [3] Cenários reais
# -------------------------------------------------
log "\n[3] Executando cenários..."

PROFILES=("URLLC" "eMBB" "mMTC")
LAT=("10ms" "50ms" "100ms")

for i in 0 1 2; do
  prof="${PROFILES[$i]}"
  lat="${LAT[$i]}"
  nsi_id="probe-${prof,,}-${TS_LOWER}"

  payload=$(cat <<JSON
{"nsiId":"${nsi_id}","serviceProfile":"${prof}","tenantId":"default","sla":{"latency":"${lat}"}}
JSON
)

  log "\n[3.$((i+1))] ${prof} → ${nsi_id}"
  echo "${payload}" > "${EVD}/payload_${prof}.json"

  post_json "${payload}" "${EVD}/resp_${prof}.json"
  cat "${EVD}/resp_${prof}.json" | tee -a "${EVD}/run.log"

  sleep 8

  # Verifica CR
  if kubectl get networksliceinstances.trisla.io -n "${NS}" "${nsi_id}" -o yaml \
    > "${EVD}/nsi_${prof}.yaml" 2>/dev/null; then

    phase=$(kubectl get networksliceinstances.trisla.io -n "${NS}" "${nsi_id}" \
      -o jsonpath='{.status.phase}' 2>/dev/null || true)

    log "phase=${phase:-<none>}"

    ns_iso="ns-${nsi_id}"
    kubectl get ns "${ns_iso}" > "${EVD}/ns_${prof}.txt" 2>/dev/null || true
    kubectl get resourcequota -n "${ns_iso}" > "${EVD}/quota_${prof}.txt" 2>/dev/null || true

    if [[ "${phase}" == "Active" ]]; then
      log "✅ PASS ${prof}"
    else
      log "⚠️ WARN ${prof} phase=${phase}"
    fi
  else
    log "❌ FAIL ${prof} (CR não criado)"
  fi
done

# -------------------------------------------------
# [4] Logs
# -------------------------------------------------
log "\n[4] Logs NASP Adapter (últimos 20 min)..."
kubectl logs -n "${NS}" deploy/trisla-nasp-adapter --since=20m \
  > "${EVD}/adapter_logs.txt"

log "\n=================================================="
log "E2E VALIDATION FINALIZADA"
log "Evidence: ${EVD}"
log "=================================================="
