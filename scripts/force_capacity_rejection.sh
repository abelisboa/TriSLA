#!/usr/bin/env bash
set -euo pipefail

NS="${1:-trisla}"
MAX="${2:-80}"
OUT_BASE="/home/porvir5g/gtp5g/trisla/evidencias_diagnostico"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
EVD="${OUT_BASE}/capacity_rejection_${TS}"
mkdir -p "${EVD}"

log() { echo -e "$@" | tee -a "${EVD}/run.log"; }

log "=================================================="
log "TriSLA — FORCE CAPACITY REJECTION"
log "Namespace : ${NS}"
log "Max Tests : ${MAX}"
log "Evidence  : ${EVD}"
log "=================================================="

kubectl -n "${NS}" port-forward svc/trisla-nasp-adapter 18086:8085 \
  > "${EVD}/pf.log" 2>&1 &
PF=$!
sleep 3

for i in $(seq 1 $MAX); do
  ID="stress-${TS}-${i}"

  python3 - <<PY > "${EVD}/resp_${i}.json" 2>/dev/null || true
import json, urllib.request
payload = {
  "nsiId": "${ID}",
  "serviceProfile": "eMBB",
  "tenantId": "default",
  "sla": {"latency": "50ms"}
}
req = urllib.request.Request(
  "http://127.0.0.1:18086/api/v1/nsi/instantiate",
  data=json.dumps(payload).encode(),
  headers={"Content-Type":"application/json"},
  method="POST"
)
try:
  with urllib.request.urlopen(req, timeout=10) as r:
    print(r.read().decode())
except Exception as e:
  print(str(e))
PY

  sleep 2

  PHASE=$(kubectl get networksliceinstances.trisla.io -n "${NS}" "${ID}" \
    -o jsonpath='{.status.phase}' 2>/dev/null || echo "none")

  log "NSI ${ID} -> phase=${PHASE}"

  if [[ "${PHASE}" == "Rejected" || "${PHASE}" == "Failed" ]]; then
    log "🚨 REJECTION DETECTED at iteration ${i}"
    break
  fi
done

kill $PF || true

log "\n=================================================="
log "TEST FINALIZADO"
log "Evidence: ${EVD}"
log "=================================================="
