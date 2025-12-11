#!/bin/bash
set -e

# ============================================
# Script de Teste Nginx - UI Dashboard
# ============================================

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "🧪 Teste Nginx - UI Dashboard"
echo "=========================================="
echo ""

# Testar UI Dashboard
echo "Testando UI Dashboard (http://localhost:80)..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:80 || echo "000")

if [ "$response" = "200" ]; then
    echo -e "${GREEN}✅ UI Dashboard está respondendo (HTTP $response)${NC}"
else
    echo -e "${RED}❌ UI Dashboard não está respondendo (HTTP $response)${NC}"
fi

# Testar API proxy
echo "Testando API proxy (http://localhost:80/api/health)..."
response=$(curl -s http://localhost:80/api/health || echo "")

if echo "$response" | grep -q "healthy\|degraded"; then
    echo -e "${GREEN}✅ API proxy está funcionando${NC}"
    echo "   Resposta: $(echo $response | jq -c . 2>/dev/null || echo $response)"
else
    echo -e "${YELLOW}⚠️  API proxy pode não estar funcionando${NC}"
    echo "   Resposta: $response"
fi

echo ""
echo "=========================================="
echo "✅ Testes Nginx concluídos"
echo "=========================================="









































