#!/usr/bin/env bash
set -euo pipefail

NS="${1:-trisla}"
OUT_BASE="/home/porvir5g/gtp5g/trisla/evidencias_diagnostico"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
EVD="${OUT_BASE}/otlp_audit_${TS}"
mkdir -p "${EVD}"

log() { echo -e "$@" | tee -a "${EVD}/run.log"; }

log "=================================================="
log "TriSLA — OTLP METRICS AUDIT"
log "Namespace : ${NS}"
log "Evidence  : ${EVD}"
log "=================================================="

POD=$(kubectl get pods -n "${NS}" -l app=trisla-nasp-adapter -o jsonpath='{.items[0].metadata.name}')

log "\n[1] OTLP endpoint env..."
kubectl exec -n "${NS}" "$POD" -- printenv | grep OTLP > "${EVD}/otlp_env.txt"

OTLP=$(grep OTLP_ENDPOINT "${EVD}/otlp_env.txt" | cut -d= -f2)

log "OTLP_ENDPOINT=${OTLP}"

HOST=$(echo "$OTLP" | awk -F[/:] '{print $4}')
PORT=$(echo "$OTLP" | awk -F: '{print $3}')

log "\n[2] TCP connectivity test..."
kubectl exec -n "${NS}" "$POD" -- sh -c "timeout 3 bash -c '</dev/tcp/${HOST}/${PORT}'" \
  > "${EVD}/tcp_test.txt" 2>&1 || true

log "\n[3] Logs export..."
kubectl logs -n "${NS}" deploy/trisla-nasp-adapter --since=20m \
  | grep -i "otlp" > "${EVD}/logs_otlp.txt" || true

log "\n=================================================="
log "AUDIT FINALIZADO"
log "Evidence: ${EVD}"
log "=================================================="
