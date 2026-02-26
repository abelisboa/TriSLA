#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="trisla"
PORTAL_SERVICE="trisla-portal-backend"
PORTAL_PORT="8001"
URL="http://${PORTAL_SERVICE}:${PORTAL_PORT}/api/v1/sla/submit"

SERVICE_TYPE="${SERVICE_TYPE:-urllc}"
TENANT_ID="${TENANT_ID:-default}"

# Timestamp compatível com RFC 1123 (sem underscore)
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
POD_NAME="e2e-submit-${TIMESTAMP}"

EVIDENCE_DIR="/home/porvir5g/gtp5g/trisla/evidencias_e2e/${TIMESTAMP}-e2e-submit-validate-bc"
mkdir -p "$EVIDENCE_DIR"

echo "=============================================="
echo "TriSLA E2E – REAL SUBMIT + BC VALIDATION"
echo "Evidence Dir: $EVIDENCE_DIR"
echo "Service Type: $SERVICE_TYPE"
echo "=============================================="

cat > "$EVIDENCE_DIR/request.json" <<EOF
{
  "template_id": "template:${SERVICE_TYPE}",
  "tenant_id": "${TENANT_ID}",
  "form_values": {
    "type": "${SERVICE_TYPE}",
    "latencia_maxima_ms": 10,
    "disponibilidade_percent": 99.99,
    "confiabilidade_percent": 99.99
  }
}
EOF

echo "🚀 Executando submit REAL..."

kubectl run ${POD_NAME} \
  -n ${NAMESPACE} \
  --image=curlimages/curl:8.6.0 \
  --restart=Never \
  --rm -i --quiet -- \
  sh -c "curl -s -X POST ${URL} \
    -H 'Content-Type: application/json' \
    --data-binary @-" \
  < "$EVIDENCE_DIR/request.json" \
  > "$EVIDENCE_DIR/response_raw.json"

echo "📥 Resposta salva."

echo "🔎 Validando resposta..."

python3 <<EOF
import json, sys

with open("${EVIDENCE_DIR}/response_raw.json") as f:
    data = json.load(f)

decision = data.get("decision")
tx_hash = data.get("tx_hash") or data.get("blockchain_tx_hash")
block_number = data.get("block_number")
status = data.get("status")

result = {
    "decision": decision,
    "status": status,
    "has_tx_hash": bool(tx_hash),
    "has_block_number": block_number is not None,
    "tx_hash": tx_hash,
    "block_number": block_number
}

print(json.dumps(result, indent=2))

if status != "ok":
    print("❌ FAIL: status != ok")
    sys.exit(1)

if decision != "ACCEPT":
    print("❌ FAIL: decision != ACCEPT")
    sys.exit(1)

if not tx_hash:
    print("❌ FAIL: tx_hash ausente")
    sys.exit(1)

if block_number is None:
    print("❌ FAIL: block_number ausente")
    sys.exit(1)

print("✅ E2E SUCCESS – Blockchain confirmado")
EOF
