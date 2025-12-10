#!/bin/bash
# Script para verificação pós-instalação do Portal TriSLA

set -e

FRONTEND_URL="http://localhost:32001"
BACKEND_URL="http://localhost:32002"

echo "🔍 Verificando Portal TriSLA..."
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para testar endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local method=${3:-GET}
    local data=${4:-""}
    local timeout=${5:-5}
    
    echo -n "Testando $name ($url)... "
    
    if [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST \
            -H "Content-Type: application/json" \
            -d "$data" \
            --max-time $timeout \
            "$url" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" \
            --max-time $timeout \
            "$url" 2>&1)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✅ OK (HTTP $http_code)${NC}"
        return 0
    else
        echo -e "${RED}❌ FALHOU (HTTP $http_code)${NC}"
        if [ -n "$body" ]; then
            echo "   Resposta: $body"
        fi
        return 1
    fi
}

# Teste 1: Backend Health Check
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TESTE 1: Backend Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if test_endpoint "Backend /health" "$BACKEND_URL/health"; then
    echo "   Resposta do /health:"
    curl -s "$BACKEND_URL/health" | jq '.' 2>/dev/null || curl -s "$BACKEND_URL/health"
    echo ""
else
    echo -e "${RED}❌ Backend não está respondendo${NC}"
    echo "   Verifique se o túnel SSH está ativo e o backend está rodando"
    exit 1
fi

# Teste 2: Frontend
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TESTE 2: Frontend"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if test_endpoint "Frontend" "$FRONTEND_URL" "GET" "" 3; then
    echo -e "${GREEN}✅ Frontend está acessível${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend pode não estar respondendo corretamente${NC}"
fi

# Teste 3: Backend NASP Diagnostics
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TESTE 3: Backend NASP Diagnostics"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if test_endpoint "Backend /nasp/diagnostics" "$BACKEND_URL/nasp/diagnostics"; then
    echo "   Diagnóstico dos módulos NASP:"
    curl -s "$BACKEND_URL/nasp/diagnostics" | jq '.' 2>/dev/null || curl -s "$BACKEND_URL/nasp/diagnostics"
    echo ""
else
    echo -e "${YELLOW}⚠️  Endpoint /nasp/diagnostics não está respondendo${NC}"
fi

# Teste 4: Validação de acesso aos módulos NASP
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TESTE 4: Validação de Acesso aos Módulos NASP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

modules=(
    "SEM-CSMF:http://trisla-sem-csmf:8080"
    "ML-NSMF:http://trisla-ml-nsmf:8081"
    "Decision Engine:http://trisla-decision-engine:8082"
    "BC-NSSMF:http://trisla-bc-nssmf:8083"
    "SLA-Agent:http://trisla-sla-agent-layer:8084"
)

for module_info in "${modules[@]}"; do
    IFS=':' read -r name url <<< "$module_info"
    echo -n "Testando $name ($url)... "
    
    # Testar com timeout de 1 segundo conforme especificação
    response=$(curl -s -w "\n%{http_code}" --max-time 1 "$url/health" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✅ Acessível${NC}"
    elif [ "$http_code" = "000" ]; then
        echo -e "${YELLOW}⚠️  Timeout ou não acessível${NC}"
    else
        echo -e "${YELLOW}⚠️  HTTP $http_code${NC}"
    fi
done

# Teste 5: Fluxo completo - POST /api/v1/sla/submit
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TESTE 5: Fluxo Completo - POST /api/v1/sla/submit"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Criar payload de teste mínimo
test_payload='{
  "tenant_id": "test-tenant",
  "sla_id": "test-sla-verify",
  "intent_text": "Test SLA for verification"
}'

echo "Enviando requisição de teste..."
if test_endpoint "POST /api/v1/sla/submit" "$BACKEND_URL/api/v1/sla/submit" "POST" "$test_payload" 10; then
    echo -e "${GREEN}✅ Fluxo completo funcionando${NC}"
else
    echo -e "${YELLOW}⚠️  Endpoint /api/v1/sla/submit pode não estar funcionando corretamente${NC}"
    echo "   Isso é esperado se os módulos NASP não estiverem totalmente configurados"
fi

# Resumo final
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 RESUMO DA VERIFICAÇÃO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 URLs de Acesso:"
echo "   Frontend: $FRONTEND_URL"
echo "   Backend:  $BACKEND_URL"
echo ""
echo "📝 Endpoints principais:"
echo "   - Backend Health:     $BACKEND_URL/health"
echo "   - NASP Diagnostics:   $BACKEND_URL/nasp/diagnostics"
echo "   - SLA Submit:         $BACKEND_URL/api/v1/sla/submit"
echo ""
echo "✅ Verificação concluída!"

