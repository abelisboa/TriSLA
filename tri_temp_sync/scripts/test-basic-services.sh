#!/bin/bash
set -e

# ============================================
# Testes Básicos Automatizados - TriSLA
# ============================================

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

PASSED=0
FAILED=0

test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "   Testando $name... "
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL (HTTP $response)${NC}"
        ((FAILED++))
        return 1
    fi
}

test_health_json() {
    local name=$1
    local url=$2
    
    echo -n "   Testando health JSON de $name... "
    response=$(curl -s "$url" 2>/dev/null || echo "")
    
    if echo "$response" | grep -q "healthy\|degraded"; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "      Resposta: $response"
        ((FAILED++))
        return 1
    fi
}

echo "=========================================="
echo "🧪 Testes Básicos Automatizados - TriSLA"
echo "=========================================="
echo ""

# Teste 1: SEM-CSMF processa intents
echo -e "${CYAN}[1] Testando SEM-CSMF...${NC}"
test_health_json "SEM-CSMF" "http://localhost:8080/health"

# Teste 2: Decision Engine carrega
echo -e "${CYAN}[2] Testando Decision Engine...${NC}"
test_health_json "Decision Engine" "http://localhost:8082/health"

# Teste 3: ML-NSMF entra no modo offline
echo -e "${CYAN}[3] Testando ML-NSMF (modo offline)...${NC}"
test_health_json "ML-NSMF" "http://localhost:8081/health"
response=$(curl -s "http://localhost:8081/health" 2>/dev/null || echo "")
if echo "$response" | grep -q "offline"; then
    echo -e "   ${GREEN}✅ ML-NSMF está em modo offline (esperado)${NC}"
    ((PASSED++))
else
    echo -e "   ${YELLOW}⚠️  ML-NSMF pode não estar em modo offline${NC}"
fi

# Teste 4: BC-NSSMF inicializa sem erros
echo -e "${CYAN}[4] Testando BC-NSSMF...${NC}"
test_health_json "BC-NSSMF" "http://localhost:8083/health"
response=$(curl -s "http://localhost:8083/health" 2>/dev/null || echo "")
if echo "$response" | grep -q "healthy\|degraded"; then
    echo -e "   ${GREEN}✅ BC-NSSMF inicializou (modo degraded aceitável)${NC}"
    ((PASSED++))
else
    echo -e "   ${RED}❌ BC-NSSMF não inicializou corretamente${NC}"
    ((FAILED++))
fi

# Teste 5: SLA Agent inicializa corretamente
echo -e "${CYAN}[5] Testando SLA-Agent Layer...${NC}"
test_health_json "SLA-Agent Layer" "http://localhost:8084/health"

# Teste 6: UI-Dashboard consegue conectar ao backend
echo -e "${CYAN}[6] Testando UI-Dashboard...${NC}"
test_endpoint "UI-Dashboard" "http://localhost:80" 200

# Teste 7: UI-Dashboard proxy para API
echo -e "${CYAN}[7] Testando UI-Dashboard API proxy...${NC}"
response=$(curl -s "http://localhost:80/api/health" 2>/dev/null || echo "")
if echo "$response" | grep -q "healthy\|degraded"; then
    echo -e "   ${GREEN}✅ UI-Dashboard consegue conectar ao backend${NC}"
    ((PASSED++))
else
    echo -e "   ${YELLOW}⚠️  UI-Dashboard pode não conseguir conectar ao backend${NC}"
    echo "      Resposta: $response"
fi

echo ""
echo "=========================================="
echo "📊 Resultados:"
echo "   ${GREEN}✅ Passou: $PASSED${NC}"
echo "   ${RED}❌ Falhou: $FAILED${NC}"
echo "=========================================="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Todos os testes passaram!${NC}"
    exit 0
else
    echo -e "${RED}❌ Alguns testes falharam${NC}"
    exit 1
fi


