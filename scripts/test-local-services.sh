#!/bin/bash
set -e

# ============================================
# Script de Teste Local - TriSLA Microserviços
# ============================================

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "🧪 Teste Local - TriSLA Microserviços"
echo "=========================================="
echo ""

# Função para testar endpoint HTTP
test_http_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Testando $name... "
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FALHOU (HTTP $response)${NC}"
        return 1
    fi
}

# Função para testar health endpoint
test_health() {
    local name=$1
    local port=$2
    
    echo -n "Testando health de $name (porta $port)... "
    response=$(curl -s "http://localhost:$port/health" || echo "")
    
    if echo "$response" | grep -q "healthy\|degraded"; then
        echo -e "${GREEN}✅ OK${NC}"
        echo "   Resposta: $(echo $response | jq -c . 2>/dev/null || echo $response)"
        return 0
    else
        echo -e "${RED}❌ FALHOU${NC}"
        echo "   Resposta: $response"
        return 1
    fi
}

# Testar cada serviço
echo "📦 Testando serviços FastAPI..."
echo ""

# BC-NSSMF (porta 8083)
if docker ps | grep -q "bc-nssmf"; then
    test_health "bc-nssmf" 8083
else
    echo -e "${YELLOW}⚠️  bc-nssmf não está rodando${NC}"
fi

# ML-NSMF (porta 8081)
if docker ps | grep -q "ml-nsmf"; then
    test_health "ml-nsmf" 8081
else
    echo -e "${YELLOW}⚠️  ml-nsmf não está rodando${NC}"
fi

# SEM-CSMF (porta 8080)
if docker ps | grep -q "sem-csmf"; then
    test_health "sem-csmf" 8080
else
    echo -e "${YELLOW}⚠️  sem-csmf não está rodando${NC}"
fi

# Decision Engine (porta 8082)
if docker ps | grep -q "decision-engine"; then
    test_health "decision-engine" 8082
else
    echo -e "${YELLOW}⚠️  decision-engine não está rodando${NC}"
fi

# SLA-Agent Layer (porta 8084)
if docker ps | grep -q "sla-agent"; then
    test_health "sla-agent-layer" 8084
else
    echo -e "${YELLOW}⚠️  sla-agent-layer não está rodando${NC}"
fi

# UI-Dashboard (porta 80)
if docker ps | grep -q "ui-dashboard"; then
    test_http_endpoint "ui-dashboard" "http://localhost:80" 200
else
    echo -e "${YELLOW}⚠️  ui-dashboard não está rodando${NC}"
fi

echo ""
echo "=========================================="
echo "✅ Testes concluídos"
echo "=========================================="





