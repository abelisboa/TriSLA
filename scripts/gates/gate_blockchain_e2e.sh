#!/bin/bash
set -e

NAMESPACE="trisla"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
EVIDENCE_DIR="/home/porvir5g/gtp5g/trisla/evidencias_gates/${TIMESTAMP}-gate-bc"
mkdir -p "$EVIDENCE_DIR"

echo "=============================================="
echo "TriSLA BLOCKCHAIN GATE – STRICT VALIDATION"
echo "Evidence Dir: $EVIDENCE_DIR"
echo "=============================================="

# 1️⃣ Verificar BC_ENABLED
echo "🔎 Verificando BC_ENABLED..."
BC_FLAG=$(kubectl exec -n $NAMESPACE deploy/trisla-bc-nssmf -- printenv | grep BC_ENABLED | cut -d= -f2)

if [ "$BC_FLAG" != "true" ]; then
  echo "❌ FAIL: BC_ENABLED != true"
  exit 1
fi
echo "✅ BC_ENABLED=true"

# 2️⃣ Verificar readiness
echo "🔎 Verificando /health/ready..."
READY=$(kubectl run -n $NAMESPACE bc-gate-check --rm -i --restart=Never \
  --image=curlimages/curl:8.6.0 -- \
  curl -s http://trisla-bc-nssmf:8083/health/ready)

echo "$READY" > "$EVIDENCE_DIR/ready.json"

RPC_CONNECTED=$(echo "$READY" | grep -c '"rpc_connected":true')

if [ "$RPC_CONNECTED" -eq 0 ]; then
  echo "❌ FAIL: RPC não conectado"
  exit 1
fi
echo "✅ RPC conectado"

# 3️⃣ Submit real
echo "🚀 Executando submit real..."

RESPONSE=$(kubectl run -n $NAMESPACE bc-gate-submit --rm -i --restart=Never \
  --image=curlimages/curl:8.6.0 -- \
  curl -s -X POST http://trisla-portal-backend:8001/api/v1/sla/submit \
  -H "Content-Type: application/json" \
  -d '{
        "template_id": "template:URLLC",
        "tenant_id": "default",
        "form_values": {
          "slice_type": "URLLC",
          "latency_maxima_ms": 10,
          "disponibilidade_percent": 99.99,
          "confiabilidade_percent": 99.99
        }
      }')

echo "$RESPONSE" > "$EVIDENCE_DIR/submit.json"

STATUS=$(echo "$RESPONSE" | grep -o '"status":"ok"' | wc -l)
TX_HASH=$(echo "$RESPONSE" | grep -o '"tx_hash":"[^"]*"' | cut -d'"' -f4)
BLOCK_NUMBER=$(echo "$RESPONSE" | grep -o '"block_number":[0-9]*' | cut -d':' -f2)

if [ "$STATUS" -eq 0 ]; then
  echo "❌ FAIL: status != ok"
  exit 1
fi

if [ -z "$TX_HASH" ]; then
  echo "❌ FAIL: tx_hash ausente"
  exit 1
fi

if [ -z "$BLOCK_NUMBER" ]; then
  echo "❌ FAIL: block_number ausente"
  exit 1
fi

echo "=============================================="
echo "✅ BLOCKCHAIN GATE PASSED"
echo "TX: $TX_HASH"
echo "Block: $BLOCK_NUMBER"
echo "=============================================="
