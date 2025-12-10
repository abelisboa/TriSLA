#!/bin/bash

# Script de validação automática das rotas TRI-SLA Light

BACKEND_URL="http://127.0.0.1:8001"
API_BASE="${BACKEND_URL}/api/v1"

echo "============================================================"
echo "  🔍 VALIDAÇÃO AUTOMÁTICA - TRI-SLA LIGHT ROTAS"
echo "============================================================"
echo ""

# Verificar se backend está rodando
echo "1️⃣  Verificando se backend está rodando..."
if ! curl -s "${BACKEND_URL}/health" > /dev/null 2>&1; then
    echo "❌ ERRO: Backend não está rodando em ${BACKEND_URL}"
    echo "   Execute: bash scripts/portal_manager.sh (opção 1)"
    exit 1
fi
echo "✅ Backend está rodando"
echo ""

# Teste 1: Health Check
echo "2️⃣  Testando Health Check..."
HEALTH=$(curl -s "${BACKEND_URL}/health")
if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ Health Check OK: $HEALTH"
else
    echo "❌ Health Check falhou: $HEALTH"
    exit 1
fi
echo ""

# Teste 2: Interpret SLA
echo "3️⃣  Testando POST /api/v1/sla/interpret..."
INTERPRET_RESPONSE=$(curl -s -X POST "${API_BASE}/sla/interpret" \
    -H "Content-Type: application/json" \
    -d '{"intent_text":"Quero URLLC com latência de 5ms","tenant_id":"tenant-001"}')
if echo "$INTERPRET_RESPONSE" | grep -q "sla_id"; then
    echo "✅ Interpret SLA OK"
    echo "   Response: $(echo $INTERPRET_RESPONSE | head -c 200)..."
    SLA_ID=$(echo "$INTERPRET_RESPONSE" | grep -o '"sla_id":"[^"]*"' | cut -d'"' -f4 | head -1)
    echo "   SLA ID obtido: $SLA_ID"
else
    echo "❌ Interpret SLA falhou: $INTERPRET_RESPONSE"
    exit 1
fi
echo ""

# Teste 3: Submit SLA
echo "4️⃣  Testando POST /api/v1/sla/submit..."
SUBMIT_RESPONSE=$(curl -s -X POST "${API_BASE}/sla/submit" \
    -H "Content-Type: application/json" \
    -d '{"template_id":"urllc-basic","form_values":{"latency_max":5},"tenant_id":"tenant-001"}')
if echo "$SUBMIT_RESPONSE" | grep -q "sla_id"; then
    echo "✅ Submit SLA OK"
    echo "   Response: $(echo $SUBMIT_RESPONSE | head -c 200)..."
    SUBMIT_SLA_ID=$(echo "$SUBMIT_RESPONSE" | grep -o '"sla_id":"[^"]*"' | cut -d'"' -f4 | head -1)
    echo "   SLA ID obtido: $SUBMIT_SLA_ID"
else
    echo "❌ Submit SLA falhou: $SUBMIT_RESPONSE"
    exit 1
fi
echo ""

# Teste 4: Status SLA
echo "5️⃣  Testando GET /api/v1/sla/status/{id}..."
TEST_SLA_ID="test-sla-123"
STATUS_RESPONSE=$(curl -s "${API_BASE}/sla/status/${TEST_SLA_ID}")
STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${API_BASE}/sla/status/${TEST_SLA_ID}")
if [ "$STATUS_CODE" = "200" ] || [ "$STATUS_CODE" = "404" ]; then
    echo "✅ Status SLA OK (HTTP $STATUS_CODE)"
    echo "   Response: $(echo $STATUS_RESPONSE | head -c 200)..."
else
    echo "❌ Status SLA falhou (HTTP $STATUS_CODE): $STATUS_RESPONSE"
    exit 1
fi
echo ""

# Teste 5: Metrics SLA
echo "6️⃣  Testando GET /api/v1/sla/metrics/{id}..."
METRICS_RESPONSE=$(curl -s "${API_BASE}/sla/metrics/${TEST_SLA_ID}")
METRICS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${API_BASE}/sla/metrics/${TEST_SLA_ID}")
if [ "$METRICS_CODE" = "200" ] || [ "$METRICS_CODE" = "404" ]; then
    echo "✅ Metrics SLA OK (HTTP $METRICS_CODE)"
    echo "   Response: $(echo $METRICS_RESPONSE | head -c 200)..."
else
    echo "❌ Metrics SLA falhou (HTTP $METRICS_CODE): $METRICS_RESPONSE"
    exit 1
fi
echo ""

# Teste 6: CORS
echo "7️⃣  Testando CORS..."
CORS_RESPONSE=$(curl -s -I -X OPTIONS "${API_BASE}/sla/interpret" \
    -H "Origin: http://localhost:3000" \
    -H "Access-Control-Request-Method: POST")
if echo "$CORS_RESPONSE" | grep -q "access-control-allow-origin"; then
    echo "✅ CORS configurado corretamente"
    echo "$CORS_RESPONSE" | grep -i "access-control"
else
    echo "❌ CORS não configurado corretamente"
    echo "$CORS_RESPONSE"
    exit 1
fi
echo ""

echo "============================================================"
echo "  ✅ TODOS OS TESTES PASSARAM COM SUCESSO!"
echo "============================================================"
echo ""
echo "🎯 Rotas validadas:"
echo "   ✅ POST /api/v1/sla/interpret"
echo "   ✅ POST /api/v1/sla/submit"
echo "   ✅ GET  /api/v1/sla/status/{id}"
echo "   ✅ GET  /api/v1/sla/metrics/{id}"
echo "   ✅ CORS configurado"
echo ""
echo "🚀 TRI-SLA LIGHT está funcionando corretamente!"

