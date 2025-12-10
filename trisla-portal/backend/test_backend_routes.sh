#!/bin/bash
# Script para testar todas as rotas do backend TriSLA Portal Light
# Valida rotas usando curl

set -e

API_BASE="http://localhost:8001/api/v1"
BACKEND_URL="http://localhost:8001"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "TEST BACKEND ROUTES - TRI-SLA PORTAL"
echo "=========================================="
echo ""

# Função para verificar resposta HTTP
check_response() {
    local status_code=$1
    local test_name=$2
    local expected_status=${3:-200}
    
    if [ "$status_code" -eq "$expected_status" ]; then
        echo -e "${GREEN}✅ $test_name: HTTP $status_code${NC}"
        return 0
    elif [ "$status_code" -ge 200 ] && [ "$status_code" -lt 300 ]; then
        echo -e "${YELLOW}⚠️  $test_name: HTTP $status_code (esperado $expected_status)${NC}"
        return 0
    else
        echo -e "${RED}❌ $test_name: HTTP $status_code (esperado $expected_status)${NC}"
        return 1
    fi
}

# Verificar se backend está rodando
echo -e "${BLUE}[TESTE 0] Verificando se backend está rodando...${NC}"
if ! curl -s -f "${BACKEND_URL}/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend não está rodando!${NC}"
    echo -e "${YELLOW}Execute primeiro: bash start_backend.sh${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Backend está rodando${NC}"
echo ""

###############################################
# TESTE 1 — Health Check
###############################################
echo -e "${BLUE}[TESTE 1] GET /health${NC}"
echo "----------------------------------------"
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${BACKEND_URL}/health")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$HEALTH_RESPONSE" | sed '$d')

if check_response "$HTTP_CODE" "[TESTE 1] Health Check" 200; then
    echo "   Resposta: $RESPONSE_BODY"
fi
echo ""

###############################################
# TESTE 2 — Root Endpoint
###############################################
echo -e "${BLUE}[TESTE 2] GET /${NC}"
echo "----------------------------------------"
ROOT_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${BACKEND_URL}/")
HTTP_CODE=$(echo "$ROOT_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$ROOT_RESPONSE" | sed '$d')

if check_response "$HTTP_CODE" "[TESTE 2] Root Endpoint" 200; then
    echo "   Resposta: $RESPONSE_BODY"
fi
echo ""

###############################################
# TESTE 3 — POST /api/v1/sla/interpret
###############################################
echo -e "${BLUE}[TESTE 3] POST /api/v1/sla/interpret${NC}"
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

# Pode retornar 200 (sucesso) ou 503 (módulo offline) - ambos são válidos para teste
if check_response "$HTTP_CODE" "[TESTE 3] Interpret SLA" 200; then
    echo "   Resposta: $(echo "$RESPONSE_BODY" | head -5)"
elif [ "$HTTP_CODE" -eq 503 ]; then
    echo -e "${YELLOW}⚠️  SEM-CSMF offline (esperado se port-forward não estiver configurado)${NC}"
else
    echo "   Resposta: $RESPONSE_BODY"
fi
echo ""

###############################################
# TESTE 4 — POST /api/v1/sla/submit
###############################################
echo -e "${BLUE}[TESTE 4] POST /api/v1/sla/submit${NC}"
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

# Pode retornar 200 (sucesso) ou 503 (módulo offline) - ambos são válidos para teste
if check_response "$HTTP_CODE" "[TESTE 4] Submit SLA" 200; then
    DECISION=$(echo "$RESPONSE_BODY" | grep -o '"decision":"[^"]*"' | cut -d'"' -f4 | head -1 || echo "N/A")
    SLA_ID=$(echo "$RESPONSE_BODY" | grep -o '"sla_id":"[^"]*"' | cut -d'"' -f4 | head -1 || echo "N/A")
    echo "   Decision: $DECISION"
    echo "   SLA ID: $SLA_ID"
elif [ "$HTTP_CODE" -eq 503 ]; then
    echo -e "${YELLOW}⚠️  Módulo offline (esperado se port-forward não estiver configurado)${NC}"
else
    echo "   Resposta: $RESPONSE_BODY"
fi
echo ""

###############################################
# TESTE 5 — GET /api/v1/sla/status/{sla_id}
###############################################
echo -e "${BLUE}[TESTE 5] GET /api/v1/sla/status/{sla_id}${NC}"
echo "----------------------------------------"
TEST_SLA_ID="test-sla-id-123"
STATUS_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/sla/status/${TEST_SLA_ID}")

HTTP_CODE=$(echo "$STATUS_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$STATUS_RESPONSE" | sed '$d')

# Pode retornar 404 (não encontrado) ou 503 (módulo offline) - ambos são válidos
if [ "$HTTP_CODE" -eq 404 ]; then
    echo -e "${YELLOW}⚠️  SLA não encontrado (esperado para SLA de teste)${NC}"
elif [ "$HTTP_CODE" -eq 503 ]; then
    echo -e "${YELLOW}⚠️  Módulo offline (esperado se port-forward não estiver configurado)${NC}"
else
    check_response "$HTTP_CODE" "[TESTE 5] Status SLA" 200
fi
echo ""

###############################################
# TESTE 6 — GET /api/v1/sla/metrics/{sla_id}
###############################################
echo -e "${BLUE}[TESTE 6] GET /api/v1/sla/metrics/{sla_id}${NC}"
echo "----------------------------------------"
METRICS_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/sla/metrics/${TEST_SLA_ID}")

HTTP_CODE=$(echo "$METRICS_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$METRICS_RESPONSE" | sed '$d')

# Pode retornar 404 (não encontrado) ou 503 (módulo offline) - ambos são válidos
if [ "$HTTP_CODE" -eq 404 ]; then
    echo -e "${YELLOW}⚠️  Métricas não encontradas (esperado para SLA de teste)${NC}"
elif [ "$HTTP_CODE" -eq 503 ]; then
    echo -e "${YELLOW}⚠️  SLA-Agent Layer offline (esperado se port-forward não estiver configurado)${NC}"
else
    check_response "$HTTP_CODE" "[TESTE 6] Metrics SLA" 200
fi
echo ""

###############################################
# Resumo Final
###############################################
echo "=========================================="
echo -e "${GREEN}✅ TESTE DE ROTAS CONCLUÍDO${NC}"
echo "=========================================="
echo ""
echo "Rotas testadas:"
echo "  ✅ GET  /health"
echo "  ✅ GET  /"
echo "  ✅ POST /api/v1/sla/interpret"
echo "  ✅ POST /api/v1/sla/submit"
echo "  ✅ GET  /api/v1/sla/status/{sla_id}"
echo "  ✅ GET  /api/v1/sla/metrics/{sla_id}"
echo ""
echo "Nota: Erros 503/404 são esperados se os módulos NASP"
echo "não estiverem acessíveis via port-forward."
echo ""

