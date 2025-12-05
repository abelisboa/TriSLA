#!/bin/bash
set -e

# ============================================
# Script de Teste Blockchain - BC-NSSMF
# ============================================

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "🧪 Teste Blockchain - BC-NSSMF"
echo "=========================================="
echo ""

# Testar health do BC-NSSMF
echo "Testando BC-NSSMF health (http://localhost:8083/health)..."
response=$(curl -s http://localhost:8083/health || echo "")

if echo "$response" | grep -q "healthy\|degraded"; then
    echo -e "${GREEN}✅ BC-NSSMF está respondendo${NC}"
    echo "   Resposta: $(echo $response | jq -c . 2>/dev/null || echo $response)"
    
    # Verificar se está em modo degraded
    if echo "$response" | grep -q "degraded"; then
        echo -e "${YELLOW}⚠️  BC-NSSMF está em modo degraded (RPC Besu não disponível)${NC}"
    fi
else
    echo -e "${RED}❌ BC-NSSMF não está respondendo${NC}"
    echo "   Resposta: $response"
fi

# Testar endpoint de contrato (se disponível)
echo ""
echo "Testando endpoint de contrato..."
response=$(curl -s -X POST http://localhost:8083/api/v1/execute-contract \
    -H "Content-Type: application/json" \
    -d '{"test": "data"}' || echo "")

if [ -n "$response" ]; then
    echo -e "${GREEN}✅ Endpoint de contrato está respondendo${NC}"
    echo "   Resposta: $(echo $response | jq -c . 2>/dev/null || echo $response)"
else
    echo -e "${YELLOW}⚠️  Endpoint de contrato não está respondendo${NC}"
fi

echo ""
echo "=========================================="
echo "✅ Testes Blockchain concluídos"
echo "=========================================="




























