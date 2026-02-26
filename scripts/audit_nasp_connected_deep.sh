#!/usr/bin/env bash
set -euo pipefail

NS="${1:-trisla}"
OUT_BASE="/home/porvir5g/gtp5g/trisla/evidencias_diagnostico"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
EVD="${OUT_BASE}/nasp_connected_${TS}"
mkdir -p "${EVD}"

log() { echo -e "$@" | tee -a "${EVD}/run.log"; }

log "=================================================="
log "TriSLA — NASP_CONNECTED DEEP AUDIT"
log "Namespace : ${NS}"
log "Evidence  : ${EVD}"
log "=================================================="

POD=$(kubectl get pods -n "${NS}" -l app=trisla-nasp-adapter -o jsonpath='{.items[0].metadata.name}')

log "\n[1] Health response..."
kubectl -n "${NS}" port-forward svc/trisla-nasp-adapter 18085:8085 \
  > "${EVD}/pf.log" 2>&1 &
PF=$!
sleep 3

python3 - <<PY > "${EVD}/health.json"
import urllib.request
print(urllib.request.urlopen("http://127.0.0.1:18085/health").read().decode())
PY

kill $PF || true

log "\n[2] Environment variables relacionadas..."
kubectl exec -n "${NS}" "$POD" -- printenv | sort > "${EVD}/env.txt"
grep -i "NASP" "${EVD}/env.txt" | tee -a "${EVD}/run.log" || true

log "\n[3] DNS resolution test..."
kubectl exec -n "${NS}" "$POD" -- getent hosts trisla-bc-nssmf \
  > "${EVD}/dns_test.txt" 2>&1 || true

log "\n[4] Logs relacionados a NASP..."
kubectl logs -n "${NS}" deploy/trisla-nasp-adapter --since=30m \
  | grep -i "nasp" > "${EVD}/logs_nasp.txt" || true

log "\n=================================================="
log "AUDIT FINALIZADO"
log "Evidence: ${EVD}"
log "=================================================="
