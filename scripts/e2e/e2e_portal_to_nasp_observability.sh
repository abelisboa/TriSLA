#!/usr/bin/env bash
set -euo pipefail

BASE="/home/porvir5g/gtp5g/trisla"
NS="trisla"
TS="$(date +%Y%m%d-%H%M%S)"
EVID="${BASE}/evidencias_e2e/${TS}-portal-nasp-observability"

PORTAL_URL="${PORTAL_URL:-http://trisla-portal-backend:8001}"
SERVICE_TYPE="${SERVICE_TYPE:-urllc}"   # urllc|embb|mmtc
TEMPLATE_ID="${TEMPLATE_ID:-template:${SERVICE_TYPE^^}}"
TENANT_ID="${TENANT_ID:-default}"

CORE_NS="${CORE_NS:-ns-1274485}"
UERANSIM_NS="${UERANSIM_NS:-ueransim}"

echo "=============================================="
echo "TriSLA E2E – PORTAL → NASP ADAPTER → OBSERVABILITY"
echo "Namespace : ${NS}"
echo "Evidence  : ${EVID}"
echo "Portal    : ${PORTAL_URL}"
echo "Service   : ${SERVICE_TYPE}"
echo "Template  : ${TEMPLATE_ID}"
echo "Core NS   : ${CORE_NS}"
echo "UERANSIM  : ${UERANSIM_NS}"
echo "=============================================="

mkdir -p "${EVID}"

# 0) Gates obrigatórios (sem duplicar lógica: chama scripts existentes)
echo "🔎 Gate A) Preflight..."
"${BASE}/scripts/gates/preflight_trisla.sh" | tee "${EVID}/gate_preflight.txt"

echo "🔎 Gate B) Blockchain Gate..."
"${BASE}/scripts/gates/gate_blockchain_e2e.sh" | tee "${EVID}/gate_blockchain.txt"

# 1) Diagnostics do Portal (fonte de verdade do encadeamento)
echo "🔎 Coletando /nasp/diagnostics..."
kubectl run -n "${NS}" diag-"${TS}" --rm -it --restart=Never --image=curlimages/curl:8.6.0 -- \
  sh -c "curl -sS ${PORTAL_URL}/nasp/diagnostics" | tee "${EVID}/portal_nasp_diagnostics.json"

# 2) Montar payload REAL do /sla/submit (sem inventar: schema do OpenAPI)
# form_values deve conter service_type (ou type/slice_type) conforme router do portal.
cat > "${EVID}/request_submit.json" <<EOF
{
  "template_id": "${TEMPLATE_ID}",
  "tenant_id": "${TENANT_ID}",
  "form_values": {
    "service_type": "${SERVICE_TYPE}",
    "type": "${SERVICE_TYPE}",
    "slice_type": "${SERVICE_TYPE}",
    "latencia_maxima_ms": "10ms",
    "throughput_min_dl_mbps": 100,
    "numero_dispositivos": 10
  }
}
EOF

# 3) Submit real (captura http_code + body)
echo "🚀 Executando submit REAL no Portal..."
kubectl run -n "${NS}" submit-"${TS}" --rm -it --restart=Never --image=curlimages/curl:8.6.0 -- \
  sh -c "curl -sS -w '\n%{http_code}' -H 'Content-Type: application/json' \
    -d @- ${PORTAL_URL}/api/v1/sla/submit" < "${EVID}/request_submit.json" \
  | tee "${EVID}/response_submit_with_code.txt"

# Separar body e code
HTTP_CODE="$(tail -n 1 "${EVID}/response_submit_with_code.txt" | tr -d '\r')"
head -n -1 "${EVID}/response_submit_with_code.txt" > "${EVID}/response_submit.json" || true

echo "🔎 HTTP_CODE=${HTTP_CODE}" | tee "${EVID}/http_code.txt"

if [ "${HTTP_CODE}" != "200" ]; then
  echo "❌ FAIL: submit não retornou 200 (code=${HTTP_CODE})"
  exit 1
fi

# 4) Validar se retornou tx_hash + block_number (sem jq, via python)
echo "🔎 Validando resposta JSON (tx_hash + block_number + decision)..."
python3 - <<PY | tee "${EVID}/validation_submit.txt"
import json, sys
p="${EVID}/response_submit.json"
try:
  data=json.load(open(p))
except Exception as e:
  print("FAIL: response não é JSON válido:", e); sys.exit(2)

decision=data.get("decision")
status=data.get("status")
tx=data.get("tx_hash") or data.get("blockchain_tx_hash")
bn=data.get("block_number")

print("decision =", decision)
print("status   =", status)
print("tx_hash  =", tx)
print("block    =", bn)

if status != "ok":
  print("FAIL: status != ok"); sys.exit(3)
if not decision:
  print("FAIL: decision ausente"); sys.exit(4)
if not tx or not isinstance(tx,str) or not tx.startswith("0x"):
  print("FAIL: tx_hash inválido"); sys.exit(5)
if bn is None or not isinstance(bn,int):
  print("FAIL: block_number inválido"); sys.exit(6)

print("PASS: submit retornou decision + tx_hash + block_number")
PY

# 5) Observabilidade por domínio (fonte verificável)
echo "📊 Coletando métricas CORE/RAN/TRANSPORTE..."
"${BASE}/scripts/obs/collect_domain_metrics.sh" \
  --evid "${EVID}" --core-ns "${CORE_NS}" --ueransim-ns "${UERANSIM_NS}" | tee "${EVID}/collect_domain_metrics.txt"

echo "=============================================="
echo "✅ E2E PORTAL→NASP→OBS PASS"
echo "Evidências: ${EVID}"
echo "=============================================="
