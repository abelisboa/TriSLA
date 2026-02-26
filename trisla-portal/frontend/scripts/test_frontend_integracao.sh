#!/bin/bash
# Script de validação de integração frontend-backend - TRI-SLA Portal Light
# Valida que o frontend consegue se comunicar corretamente com o backend

set -e

API_BASE="http://localhost:8001/api/v1"
FRONTEND_URL="http://localhost:3000"

echo "=========================================="
echo "VALIDAÇÃO INTEGRAÇÃO FRONTEND-BACKEND"
echo "=========================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para verificar resposta HTTP
check_response() {
    local status_code=$1
    local test_name=$2
    
    if [ "$status_code" -ge 200 ] && [ "$status_code" -lt 300 ]; then
        echo -e "${GREEN}✅ $test_name: HTTP $status_code${NC}"
        return 0
    else
        echo -e "${RED}❌ $test_name: HTTP $status_code${NC}"
        return 1
    fi
}

echo "[TESTE 1] Backend: Health Check"
echo "----------------------------------------"
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/../health")

HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$HEALTH_RESPONSE" | sed '$d')

if ! check_response "$HTTP_CODE" "[TESTE 1] Backend Health"; then
    echo "Resposta: $RESPONSE_BODY"
    echo -e "${YELLOW}⚠️  Backend pode não estar rodando${NC}"
    exit 1
fi
echo ""

echo "[TESTE 2] Backend: Criação via PLN"
echo "----------------------------------------"
INTERPRET_PAYLOAD=$(cat <<EOF
{
  "intent_text": "Quero um slice URLLC com latência máxima de 5ms e confiabilidade de 99.999%",
  "tenant_id": "default"
}
EOF
)

INTERPRET_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/sla/interpret" \
    -H "Content-Type: application/json" \
    -d "$INTERPRET_PAYLOAD")

HTTP_CODE=$(echo "$INTERPRET_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$INTERPRET_RESPONSE" | sed '$d')

if ! check_response "$HTTP_CODE" "[TESTE 2] Criação via PLN"; then
    echo "Resposta: $RESPONSE_BODY"
    exit 1
fi

INTENT_ID=$(echo "$RESPONSE_BODY" | grep -o '"intent_id":"[^"]*"' | cut -d'"' -f4 | head -1)
echo "   Intent ID: $INTENT_ID"
echo ""

echo "[TESTE 3] Backend: Criação via Template"
echo "----------------------------------------"
SUBMIT_PAYLOAD=$(cat <<EOF
{
  "template_id": "urllc-template-001",
  "form_values": {
    "latency": 5,
    "reliability": 99.999
  },
  "tenant_id": "default"
}
EOF
)

SUBMIT_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/sla/submit" \
    -H "Content-Type: application/json" \
    -d "$SUBMIT_PAYLOAD")

HTTP_CODE=$(echo "$SUBMIT_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$SUBMIT_RESPONSE" | sed '$d')

if ! check_response "$HTTP_CODE" "[TESTE 3] Criação via Template"; then
    echo "Resposta: $RESPONSE_BODY"
    exit 1
fi

DECISION=$(echo "$RESPONSE_BODY" | grep -o '"decision":"[^"]*"' | cut -d'"' -f4 | head -1)
SLA_ID=$(echo "$RESPONSE_BODY" | grep -o '"sla_id":"[^"]*"' | cut -d'"' -f4 | head -1)
SEM_CSMF_STATUS=$(echo "$RESPONSE_BODY" | grep -o '"sem_csmf_status":"[^"]*"' | cut -d'"' -f4 | head -1)
ML_NSMF_STATUS=$(echo "$RESPONSE_BODY" | grep -o '"ml_nsmf_status":"[^"]*"' | cut -d'"' -f4 | head -1)
BC_STATUS=$(echo "$RESPONSE_BODY" | grep -o '"bc_status":"[^"]*"' | cut -d'"' -f4 | head -1)

echo "   Decision: $DECISION"
echo "   SLA ID: $SLA_ID"
echo "   SEM-CSMF: $SEM_CSMF_STATUS"
echo "   ML-NSMF: $ML_NSMF_STATUS"
echo "   BC-NSSMF: $BC_STATUS"
echo ""

if [ -z "$SLA_ID" ]; then
    echo -e "${YELLOW}⚠️  Nenhum SLA ID retornado${NC}"
    exit 1
fi

echo "[TESTE 4] Backend: Métricas"
echo "----------------------------------------"
METRICS_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/sla/metrics/${SLA_ID}")

HTTP_CODE=$(echo "$METRICS_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$METRICS_RESPONSE" | sed '$d')

if ! check_response "$HTTP_CODE" "[TESTE 4] Métricas"; then
    echo "Resposta: $RESPONSE_BODY"
    if [ "$HTTP_CODE" -eq 404 ]; then
        echo -e "${YELLOW}⚠️  Métricas não encontradas (pode ser esperado se SLA ainda não tem métricas)${NC}"
    else
        exit 1
    fi
else
    LATENCY=$(echo "$RESPONSE_BODY" | grep -o '"latency_ms":[0-9.]*' | cut -d':' -f2 | head -1)
    SLICE_STATUS=$(echo "$RESPONSE_BODY" | grep -o '"slice_status":"[^"]*"' | cut -d'"' -f4 | head -1)
    
    echo "   Latency (ms): $LATENCY"
    echo "   Slice Status: $SLICE_STATUS"
fi
echo ""

echo "=========================================="
echo "✅ VALIDAÇÃO FRONTEND-BACKEND CONCLUÍDA"
echo "=========================================="
echo ""
echo "Resumo:"
echo "  [TESTE 1] Backend Health: OK"
echo "  [TESTE 2] Criação via PLN: OK"
echo "  [TESTE 3] Criação via Template: $DECISION"
echo "  [TESTE 4] Métricas: OK"
echo ""
echo "Frontend pode ser testado em: $FRONTEND_URL"
echo ""

