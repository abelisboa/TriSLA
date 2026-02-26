#!/usr/bin/env bash
set -euo pipefail

NS="${1:-trisla}"
MAX="${2:-120}"
OUT_BASE="/home/porvir5g/gtp5g/trisla/evidencias_diagnostico"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
TSL="$(echo "$TS" | tr '[:upper:]' '[:lower:]')"
EVD="${OUT_BASE}/capacity_rejection_v2_${TS}"
mkdir -p "${EVD}"

log() { echo -e "$@" | tee -a "${EVD}/run.log"; }

log "=================================================="
log "TriSLA — FORCE CAPACITY REJECTION v2 (AUDIT-READY)"
log "Namespace : ${NS}"
log "Max Tests : ${MAX}"
log "Evidence  : ${EVD}"
log "=================================================="

# Port-forward robusto
kubectl -n "${NS}" port-forward svc/trisla-nasp-adapter 18086:8085 > "${EVD}/pf.log" 2>&1 &
PF=$!
sleep 2

# Aguarda porta responder
python3 - <<'PY' > "${EVD}/pf_ready.txt" 2>&1 || true
import socket, time
for i in range(1,31):
    s=socket.socket()
    try:
        s.settimeout(1)
        s.connect(("127.0.0.1",18086))
        print("PORT_READY", i)
        break
    except Exception as e:
        time.sleep(0.2)
    finally:
        s.close()
PY

if ! grep -q "PORT_READY" "${EVD}/pf_ready.txt"; then
  log "❌ FAIL: port-forward não subiu (ver pf.log e pf_ready.txt)"
  kill $PF >/dev/null 2>&1 || true
  exit 1
fi
log "✅ port-forward pronto"

FAIL_AT=0

for i in $(seq 1 "$MAX"); do
  ID="stress-${TSL}-${i}"   # RFC1123 lowercase
  RESP="${EVD}/resp_${i}.json"
  META="${EVD}/meta_${i}.txt"

  # POST com captura de status code
  python3 - <<PY > "$RESP" 2>&1 || true
import json, urllib.request, urllib.error
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
    body = r.read().decode()
    print("HTTP_STATUS", r.status)
    print(body)
except urllib.error.HTTPError as e:
  print("HTTP_STATUS", e.code)
  print(e.read().decode())
except Exception as e:
  print("EXCEPTION", str(e))
PY

  HTTP_STATUS="$(grep -m1 'HTTP_STATUS' "$RESP" | awk '{print $2}' || true)"
  echo "id=${ID} http=${HTTP_STATUS:-na}" > "$META"

  # Confirma CR criado
  if kubectl get networksliceinstances.trisla.io -n "${NS}" "${ID}" >/dev/null 2>&1; then
    PHASE="$(kubectl get networksliceinstances.trisla.io -n "${NS}" "${ID}" -o jsonpath='{.status.phase}' 2>/dev/null || echo "")"
    log "NSI ${ID} -> http=${HTTP_STATUS:-na} phase=${PHASE:-empty}"
  else
    log "NSI ${ID} -> http=${HTTP_STATUS:-na} CR=NOT_CREATED"
  fi

  # Critérios de “rejeição detectada”
  if [[ "${HTTP_STATUS:-}" == "409" || "${HTTP_STATUS:-}" == "422" || "${HTTP_STATUS:-}" == "429" || "${HTTP_STATUS:-}" == "503" ]]; then
    log "🚨 STOP: falha HTTP detectada na iteração ${i} (ver ${RESP})"
    FAIL_AT=$i
    break
  fi

  if kubectl get networksliceinstances.trisla.io -n "${NS}" "${ID}" >/dev/null 2>&1; then
    PHASE="$(kubectl get networksliceinstances.trisla.io -n "${NS}" "${ID}" -o jsonpath='{.status.phase}' 2>/dev/null || echo "")"
    if [[ "${PHASE}" == "Rejected" || "${PHASE}" == "Failed" ]]; then
      log "🚨 STOP: rejeição por capacidade detectada na iteração ${i} (phase=${PHASE})"
      FAIL_AT=$i
      break
    fi
  fi

  sleep 1
done

kill $PF >/dev/null 2>&1 || true

log "\n=================================================="
log "FINALIZADO"
log "FAIL_AT=${FAIL_AT}"
log "Evidence: ${EVD}"
log "=================================================="
