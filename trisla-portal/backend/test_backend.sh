#!/bin/bash
# Script para testar backend TriSLA Portal Light
# Valida todas as rotas e funcionalidades

set -e

API_BASE="http://localhost:8001/api/v1"
BACKEND_URL="http://localhost:8001"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "TEST BACKEND - TRI-SLA PORTAL"
echo "=========================================="
echo ""

# Verificar se backend está rodando
echo -e "${BLUE}[TESTE 0] Verificando backend...${NC}"
if ! curl -s -f "${BACKEND_URL}/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend não está rodando!${NC}"
    echo -e "${YELLOW}Execute: bash start_backend.sh${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Backend está rodando${NC}"
echo ""

# Função para testar endpoint
test_endpoint() {
    local method=$1
    local url=$2
    local expected_status=$3
    local payload=$4
    local test_name=$5
    
    echo -e "${BLUE}[$test_name] $method $url${NC}"
    
    if [ "$method" = "GET" ]; then
        RESPONSE=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null || echo -e "\n000")
    else
        RESPONSE=$(curl -s -w "\n%{http_code}" -X "$method" "$url" \
            -H "Content-Type: application/json" \
            -d "$payload" 2>/dev/null || echo -e "\n000")
    fi
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" = "$expected_status" ]; then
        echo -e "${GREEN}✅ HTTP $HTTP_CODE (esperado $expected_status)${NC}"
        return 0
    elif [ "$HTTP_CODE" = "503" ]; then
        echo -e "${YELLOW}⚠️  HTTP $HTTP_CODE - Módulo offline (esperado sem port-forward)${NC}"
        return 2
    else
        echo -e "${RED}❌ HTTP $HTTP_CODE (esperado $expected_status)${NC}"
        return 1
    fi
}

# Teste 1: Health Check
test_endpoint "GET" "${BACKEND_URL}/health" "200" "" "TESTE 1"
echo ""

# Teste 2: Root Endpoint
test_endpoint "GET" "${BACKEND_URL}/" "200" "" "TESTE 2"
echo ""

# Teste 3: Interpret
INTERPRET_PAYLOAD='{"intent_text":"Quero um slice URLLC com latência máxima de 5ms","tenant_id":"default"}'
test_endpoint "POST" "${API_BASE}/sla/interpret" "200" "$INTERPRET_PAYLOAD" "TESTE 3"
echo ""

# Teste 4: Submit
SUBMIT_PAYLOAD='{"template_id":"urllc-template-001","form_values":{"latency":5,"reliability":99.999},"tenant_id":"default"}'
test_endpoint "POST" "${API_BASE}/sla/submit" "200" "$SUBMIT_PAYLOAD" "TESTE 4"
echo ""

# Teste 5: Status
test_endpoint "GET" "${API_BASE}/sla/status/test-sla-123" "404" "" "TESTE 5"
echo ""

# Teste 6: Metrics
test_endpoint "GET" "${API_BASE}/sla/metrics/test-sla-123" "404" "" "TESTE 6"
echo ""

echo "=========================================="
echo -e "${GREEN}✅ TESTES CONCLUÍDOS${NC}"
echo "=========================================="
echo ""
echo "Nota: Erros 503/404 são esperados se os módulos NASP"
echo "não estiverem acessíveis via port-forward."
echo ""
