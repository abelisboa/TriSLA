#!/bin/bash
# ===========================================================
# 🔍 TriSLA Portal Verification Script
# Verifica a comunicação entre UI, API e módulos Core reais
# ===========================================================

API_URL="http://localhost:8000"
UI_URL="http://localhost:5173"

echo "==============================================="
echo "🔎 TriSLA Portal – Environment Validation"
echo "==============================================="
echo "Checking connections at: $(date)"
echo

function check_endpoint() {
  local NAME=$1
  local URL=$2
  echo -n "🔗 Testing $NAME at $URL ... "
  if curl -s --max-time 10 -o /dev/null -w "%{http_code}" "$URL" | grep -q "200"; then
    echo "✅ OK"
  else
    echo "❌ Failed"
  fi
}

# 1️⃣ API health
check_endpoint "TriSLA API health" "$API_URL/api/v1/health"

# 2️⃣ Semantic module
echo -n "🧠 Testing SEM-NSMF (semantic) → "
curl -s -X POST "$API_URL/api/v1/semantic" \
  -H "Content-Type: application/json" \
  -d '{"descricao":"cirurgia remota 5G"}' | jq || echo "❌ Semantic module not responding"

# 3️⃣ AI prediction
echo -n "🤖 Testing ML-NSMF (AI prediction) → "
curl -s -X POST "$API_URL/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{"slice_type":"URLLC","qos":{"latency":5}}' | jq || echo "❌ AI module not responding"

# 4️⃣ Blockchain contract
echo -n "🔗 Testing BC-NSSMF (blockchain contract) → "
curl -s -X POST "$API_URL/api/v1/contracts" \
  -H "Content-Type: application/json" \
  -d '{"descricao":"teste de contrato"}' | jq || echo "❌ Blockchain module not responding"

# 5️⃣ Monitoring metrics
echo -n "📊 Testing NWDAF-like (monitoring) → "
curl -s "$API_URL/api/v1/metrics" | jq || echo "❌ Monitoring module not responding"

# 6️⃣ UI check
check_endpoint "TriSLA UI" "$UI_URL"

echo
echo "==============================================="
echo "✅ Validation completed!"
echo "==============================================="
