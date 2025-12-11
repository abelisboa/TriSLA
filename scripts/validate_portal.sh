#!/bin/bash
# Script de validação do TriSLA Portal
# Testa todas as rotas principais

set -e

API_BASE="http://localhost:8001/api/v1"
BACKEND_URL="http://localhost:8001"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "VALIDAÇÃO COMPLETA - TRI-SLA PORTAL"
echo "=========================================="
echo ""

# Verificar se backend está rodando
echo -e "${BLUE}[1] Verificando backend...${NC}"
if ! curl -s -f "${BACKEND_URL}/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend não está rodando!${NC}"
    echo -e "${YELLOW}Execute: cd trisla-portal/backend && bash start_backend.sh${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Backend está rodando${NC}"
echo ""

# Teste 1: Health Check
echo -e "${BLUE}[2] Testando GET /health${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" "${BACKEND_URL}/health")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✅ Health check: OK${NC}"
else
    echo -e "${RED}❌ Health check: HTTP $HTTP_CODE${NC}"
fi
echo ""

# Teste 2: Interpret PLN
echo -e "${BLUE}[3] Testando POST /api/v1/sla/interpret${NC}"
INTERPRET_PAYLOAD='{"intent_text":"cirurgia remota","tenant_id":"default"}'
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/sla/interpret" \
    -H "Content-Type: application/json" \
    -d "$INTERPRET_PAYLOAD")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✅ Interpret: OK${NC}"
    INTENT_ID=$(echo "$RESPONSE_BODY" | grep -o '"intent_id":"[^"]*"' | cut -d'"' -f4 | head -1 || echo "N/A")
    SERVICE_TYPE=$(echo "$RESPONSE_BODY" | grep -o '"service_type":"[^"]*"' | cut -d'"' -f4 | head -1 || echo "N/A")
    echo "   Intent ID: $INTENT_ID"
    echo "   Service Type: $SERVICE_TYPE"
elif [ "$HTTP_CODE" -eq 503 ]; then
    echo -e "${YELLOW}⚠️  Interpret: SEM-CSMF offline (esperado sem port-forward)${NC}"
else
    echo -e "${RED}❌ Interpret: HTTP $HTTP_CODE${NC}"
    echo "   Resposta: $RESPONSE_BODY"
fi
echo ""

# Teste 3: Submit Template
echo -e "${BLUE}[4] Testando POST /api/v1/sla/submit${NC}"
SUBMIT_PAYLOAD='{"template_id":"urllc-template-001","form_values":{"type":"URLLC","latency":5,"reliability":99.999},"tenant_id":"default"}'
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/sla/submit" \
    -H "Content-Type: application/json" \
    -d "$SUBMIT_PAYLOAD")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✅ Submit: OK${NC}"
    DECISION=$(echo "$RESPONSE_BODY" | grep -o '"decision":"[^"]*"' | cut -d'"' -f4 | head -1 || echo "N/A")
    SLA_ID=$(echo "$RESPONSE_BODY" | grep -o '"sla_id":"[^"]*"' | cut -d'"' -f4 | head -1 || echo "N/A")
    SERVICE_TYPE=$(echo "$RESPONSE_BODY" | grep -o '"service_type":"[^"]*"' | cut -d'"' -f4 | head -1 || echo "N/A")
    echo "   Decision: $DECISION"
    echo "   SLA ID: $SLA_ID"
    echo "   Service Type: $SERVICE_TYPE"
elif [ "$HTTP_CODE" -eq 503 ]; then
    echo -e "${YELLOW}⚠️  Submit: Módulo offline (esperado sem port-forward)${NC}"
else
    echo -e "${RED}❌ Submit: HTTP $HTTP_CODE${NC}"
    echo "   Resposta: $(echo "$RESPONSE_BODY" | head -c 200)..."
fi
echo ""

# Teste 4: Status
echo -e "${BLUE}[5] Testando GET /api/v1/sla/status/test-sla-123${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" "${API_BASE}/sla/status/test-sla-123")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" -eq 404 ]; then
    echo -e "${GREEN}✅ Status: 404 (esperado - SLA não existe)${NC}"
else
    echo -e "${YELLOW}⚠️  Status: HTTP $HTTP_CODE${NC}"
fi
echo ""

# Teste 5: Metrics
echo -e "${BLUE}[6] Testando GET /api/v1/sla/metrics/test-sla-123${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" "${API_BASE}/sla/metrics/test-sla-123")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" -eq 404 ] || [ "$HTTP_CODE" -eq 503 ]; then
    echo -e "${GREEN}✅ Metrics: HTTP $HTTP_CODE (esperado - SLA não existe ou módulo offline)${NC}"
else
    echo -e "${YELLOW}⚠️  Metrics: HTTP $HTTP_CODE${NC}"
fi
echo ""

echo "=========================================="
echo -e "${GREEN}✅ VALIDAÇÃO CONCLUÍDA${NC}"
echo "=========================================="
echo ""
echo "Nota: Erros 503/404 são esperados se os módulos NASP"
echo "não estiverem acessíveis via port-forward."
echo ""

