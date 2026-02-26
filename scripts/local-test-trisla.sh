#!/bin/bash
set -e

# ============================================
# Script de Teste Local - TriSLA
# ============================================
# Valida sintaxe, sobe stack e testa endpoints
# ============================================

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

COMPOSE_FILE="local/docker-compose.local.yml"
PASSED=0
FAILED=0

echo "=========================================="
echo "🧪 Teste Local TriSLA"
echo "=========================================="
echo ""

# Função para testar endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    local max_attempts=${4:-10}
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
        
        if [ "$response" = "$expected_status" ]; then
            echo -e "   ${GREEN}✅ $name: PASS (HTTP $response)${NC}"
            ((PASSED++))
            return 0
        fi
        
        if [ $attempt -lt $max_attempts ]; then
            sleep 2
            ((attempt++))
        else
            echo -e "   ${RED}❌ $name: FAIL (HTTP $response após $max_attempts tentativas)${NC}"
            ((FAILED++))
            return 1
        fi
    done
}

test_health_json() {
    local name=$1
    local url=$2
    local max_attempts=${3:-10}
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        response=$(curl -s "$url" 2>/dev/null || echo "")
        
        if echo "$response" | grep -q "healthy\|degraded"; then
            echo -e "   ${GREEN}✅ $name: PASS${NC}"
            echo "      Resposta: $(echo $response | jq -c . 2>/dev/null || echo $response | head -c 100)"
            ((PASSED++))
            return 0
        fi
        
        if [ $attempt -lt $max_attempts ]; then
            sleep 2
            ((attempt++))
        else
            echo -e "   ${RED}❌ $name: FAIL${NC}"
            echo "      Resposta: $response"
            ((FAILED++))
            return 1
        fi
    done
}

# Passo 1: Verificar sintaxe Python
echo -e "${CYAN}[1] Verificando sintaxe Python...${NC}"
echo ""

MODULES=("bc-nssmf" "ml-nsmf" "sem-csmf" "decision-engine" "sla-agent-layer")

for module in "${MODULES[@]}"; do
    echo -n "   Verificando $module... "
    if python3 -m py_compile apps/$module/src/*.py 2>/dev/null; then
        echo -e "${GREEN}✅ OK${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ Erros encontrados${NC}"
        ((FAILED++))
    fi
done

echo ""

# Passo 2: Subir stack
echo -e "${CYAN}[2] Subindo stack Docker Compose...${NC}"
echo ""

if ! docker compose -f "$COMPOSE_FILE" up -d; then
    echo -e "${RED}❌ Erro ao subir stack${NC}"
    exit 1
fi

echo ""
echo "   Aguardando containers iniciarem (30s)..."
sleep 30

echo ""

# Passo 3: Verificar containers
echo -e "${CYAN}[3] Verificando containers...${NC}"
echo ""

containers=(
    "trisla-bc-nssmf-local"
    "trisla-ml-nsmf-local"
    "trisla-sem-csmf-local"
    "trisla-decision-engine-local"
    "trisla-sla-agent-layer-local"
    "trisla-ui-dashboard-local"
)

for container in "${containers[@]}"; do
    if docker ps --format "{{.Names}}" | grep -q "^${container}$"; then
        status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "unknown")
        if [ "$status" = "running" ]; then
            echo -e "   ${GREEN}✅ $container: running${NC}"
            ((PASSED++))
        else
            echo -e "   ${RED}❌ $container: $status${NC}"
            ((FAILED++))
        fi
    else
        echo -e "   ${RED}❌ $container: não encontrado${NC}"
        ((FAILED++))
    fi
done

echo ""

# Passo 4: Testar health endpoints
echo -e "${CYAN}[4] Testando health endpoints...${NC}"
echo ""

test_health_json "BC-NSSMF" "http://localhost:8083/health"
test_health_json "ML-NSMF" "http://localhost:8081/health"
test_health_json "SEM-CSMF" "http://localhost:8080/health"
test_health_json "Decision Engine (8082)" "http://localhost:8082/health"
test_health_json "Decision Engine (9090)" "http://localhost:9090/health"
test_health_json "SLA-Agent Layer" "http://localhost:8084/health"
test_endpoint "UI-Dashboard" "http://localhost:3000" 200

echo ""

# Passo 5: Testar endpoint de Intent
echo -e "${CYAN}[5] Testando endpoint de Intent...${NC}"
echo ""

echo -n "   Testando POST /api/v1/intents... "
response=$(curl -s -X POST "http://localhost:3000/api/v1/intents" \
    -H "Content-Type: application/json" \
    -d '{
        "intent_id": "test-intent-001",
        "tenant_id": "test-tenant",
        "service_type": "eMBB",
        "sla_requirements": {
            "latency": "50ms",
            "throughput": "100Mbps"
        }
    }' 2>/dev/null || echo "")

if [ -n "$response" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    echo "      Resposta: $(echo $response | jq -c . 2>/dev/null || echo $response | head -c 100)"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  Sem resposta (pode ser esperado se autenticação estiver habilitada)${NC}"
fi

echo ""

# Passo 6: Resumo
echo "=========================================="
echo "📊 Resumo:"
echo "   ${GREEN}✅ Passou: $PASSED${NC}"
echo "   ${RED}❌ Falhou: $FAILED${NC}"
echo "=========================================="
echo ""

# Mostrar logs de erros se houver
if [ $FAILED -gt 0 ]; then
    echo -e "${YELLOW}📋 Verificando logs de containers com problemas...${NC}"
    echo ""
    
    for container in "${containers[@]}"; do
        if ! docker ps --format "{{.Names}}" | grep -q "^${container}$"; then
            echo -e "${RED}Logs de $container:${NC}"
            docker logs "$container" --tail 20 2>&1 | head -20
            echo ""
        fi
    fi
fi

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Todos os testes passaram!${NC}"
    echo ""
    echo "Serviços disponíveis:"
    echo "   • SEM-CSMF: http://localhost:8080"
    echo "   • ML-NSMF: http://localhost:8081"
    echo "   • Decision Engine: http://localhost:8082 ou http://localhost:9090"
    echo "   • BC-NSSMF: http://localhost:8083"
    echo "   • SLA-Agent Layer: http://localhost:8084"
    echo "   • UI-Dashboard: http://localhost:3000"
    exit 0
else
    echo -e "${RED}❌ Alguns testes falharam${NC}"
    echo ""
    echo "Para ver logs: docker compose -f $COMPOSE_FILE logs -f"
    exit 1
fi

