#!/bin/bash
set -e

API="http://127.0.0.1:8001/api/v1/sla"

echo "============================================================"
echo "   🔍 VALIDAÇÃO AUTOMÁTICA — TRI-SLA LIGHT (Backend)"
echo "============================================================"

echo ""
echo "1️⃣  Testando health check..."
curl -s http://127.0.0.1:8001/api/v1/health || {
    echo "❌ Backend não está respondendo."
    exit 1
}

echo "✔ Health OK"
echo ""

echo "2️⃣  Testando rota /interpret..."
curl -s -X POST "$API/interpret" \
  -H "Content-Type: application/json" \
  -d '{"intent_text":"Quero um slice URLLC com 5ms"}' || {
    echo "❌ Falha na rota /interpret"
    exit 1
}

echo "✔ Rota interpret OK"
echo ""

echo "3️⃣  Testando rota /submit..."
curl -s -X POST "$API/submit" \
  -H "Content-Type: application/json" \
  -d '{"type":"URLLC","latency_ms":5}' || {
    echo "❌ Falha na rota /submit"
    exit 1
}

echo "✔ Rota submit OK"
echo ""

echo "4️⃣  Testando rota /metrics..."
curl -s "$API/metrics/test-sla" || {
    echo "❌ Falha na rota /metrics"
    exit 1
}

echo "✔ Rota metrics OK"
echo ""
echo "============================================================"
echo "   ✅ TODAS AS ROTAS DO TRI-SLA LIGHT ESTÃO FUNCIONANDO"
echo "============================================================"
