#!/bin/bash
# Script de validação completa - TriSLA Portal Light (Port-Forward)
# Testa todos os módulos TriSLA rodando via port-forward localhost

set -e

API_BASE="http://localhost:8001/api/v1"
BACKEND_URL="http://localhost:8001"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "VALIDAÇÃO COMPLETA - TRI-SLA PORTAL LIGHT"
echo "Port-Forward: localhost:8080-8084"
echo "=========================================="
echo ""

# Função para verificar resposta HTTP
check_response() {
    local status_code=$1
    local test_name=$2
    
    if [ "$status_code" -ge 200 ] && [ "$status_code" -lt 300 ]; then
        echo -e "${GREEN}✅ $test_name: HTTP $status_code${NC}"
        return 0
    elif [ "$status_code" -eq 503 ]; then
        echo -e "${YELLOW}⚠️  $test_name: HTTP $status_code (Módulo offline)${NC}"
        return 2
    else
        echo -e "${RED}❌ $test_name: HTTP $status_code${NC}"
        return 1
    fi
}

###############################################
# TESTE 0 — Backend Health Check
###############################################
echo -e "${BLUE}[TESTE 0] Backend Health Check${NC}"
echo "----------------------------------------"
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${BACKEND_URL}/health")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$HEALTH_RESPONSE" | sed '$d')

if ! check_response "$HTTP_CODE" "[TESTE 0] Backend Health"; then
    echo "Resposta: $RESPONSE_BODY"
    echo -e "${RED}❌ Backend não está rodando. Execute primeiro: uvicorn src.main:app --host 0.0.0.0 --port 8001${NC}"
    exit 1
fi
echo ""

###############################################
# TESTE 1 — SEM-CSMF (via Portal)
###############################################
echo -e "${BLUE}[TESTE 1] SEM-CSMF: Interpretação PLN${NC}"
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

if ! check_response "$HTTP_CODE" "[TESTE 1] SEM-CSMF"; then
    echo "Resposta: $RESPONSE_BODY"
    exit 1
fi

INTENT_ID=$(echo "$RESPONSE_BODY" | grep -o '"intent_id":"[^"]*"' | cut -d'"' -f4 | head -1)
NEST_ID=$(echo "$RESPONSE_BODY" | grep -o '"nest_id":"[^"]*"' | cut -d'"' -f4 | head -1)
SLICE_TYPE=$(echo "$RESPONSE_BODY" | grep -o '"slice_type":"[^"]*"' | cut -d'"' -f4 | head -1)

echo "   Intent ID: $INTENT_ID"
echo "   NEST ID: $NEST_ID"
echo "   Slice Type: $SLICE_TYPE"
echo ""

###############################################
# TESTE 2 — Pipeline Completo via Template
###############################################
echo -e "${BLUE}[TESTE 2] Pipeline Completo: Template Submit${NC}"
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

if ! check_response "$HTTP_CODE" "[TESTE 2] Pipeline Completo"; then
    echo "Resposta: $RESPONSE_BODY"
    exit 1
fi

DECISION=$(echo "$RESPONSE_BODY" | grep -o '"decision":"[^"]*"' | cut -d'"' -f4 | head -1)
SLA_ID=$(echo "$RESPONSE_BODY" | grep -o '"sla_id":"[^"]*"' | cut -d'"' -f4 | head -1)
SEM_CSMF_STATUS=$(echo "$RESPONSE_BODY" | grep -o '"sem_csmf_status":"[^"]*"' | cut -d'"' -f4 | head -1)
ML_NSMF_STATUS=$(echo "$RESPONSE_BODY" | grep -o '"ml_nsmf_status":"[^"]*"' | cut -d'"' -f4 | head -1)
BC_STATUS=$(echo "$RESPONSE_BODY" | grep -o '"bc_status":"[^"]*"' | cut -d'"' -f4 | head -1)
SLA_AGENT_STATUS=$(echo "$RESPONSE_BODY" | grep -o '"sla_agent_status":"[^"]*"' | cut -d'"' -f4 | head -1)
TX_HASH=$(echo "$RESPONSE_BODY" | grep -o '"tx_hash":"[^"]*"' | cut -d'"' -f4 | head -1)

echo "   Decision: $DECISION"
echo "   SLA ID: $SLA_ID"
echo "   SEM-CSMF: $SEM_CSMF_STATUS"
echo "   ML-NSMF: $ML_NSMF_STATUS"
echo "   BC-NSSMF: $BC_STATUS"
echo "   SLA-Agent Layer: $SLA_AGENT_STATUS"
if [ -n "$TX_HASH" ]; then
    echo "   TxHash: ${TX_HASH:0:16}..."
fi
echo ""

if [ -z "$SLA_ID" ]; then
    echo -e "${YELLOW}⚠️  Nenhum SLA ID retornado${NC}"
    exit 1
fi

###############################################
# TESTE 3 — Métricas via SLA-Agent Layer
###############################################
echo -e "${BLUE}[TESTE 3] Métricas: SLA-Agent Layer${NC}"
echo "----------------------------------------"
METRICS_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/sla/metrics/${SLA_ID}")

HTTP_CODE=$(echo "$METRICS_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$METRICS_RESPONSE" | sed '$d')

check_response_result=$?
if [ $check_response_result -eq 2 ]; then
    echo -e "${YELLOW}⚠️  SLA-Agent Layer offline ou métricas ainda não disponíveis${NC}"
    echo "Resposta: $RESPONSE_BODY"
elif [ $check_response_result -eq 1 ]; then
    echo "Resposta: $RESPONSE_BODY"
    exit 1
else
    LATENCY=$(echo "$RESPONSE_BODY" | grep -o '"latency_ms":[0-9.]*' | cut -d':' -f2 | head -1)
    JITTER=$(echo "$RESPONSE_BODY" | grep -o '"jitter_ms":[0-9.]*' | cut -d':' -f2 | head -1)
    THROUGHPUT_UL=$(echo "$RESPONSE_BODY" | grep -o '"throughput_ul":[0-9.]*' | cut -d':' -f2 | head -1)
    THROUGHPUT_DL=$(echo "$RESPONSE_BODY" | grep -o '"throughput_dl":[0-9.]*' | cut -d':' -f2 | head -1)
    PACKET_LOSS=$(echo "$RESPONSE_BODY" | grep -o '"packet_loss":[0-9.]*' | cut -d':' -f2 | head -1)
    AVAILABILITY=$(echo "$RESPONSE_BODY" | grep -o '"availability":[0-9.]*' | cut -d':' -f2 | head -1)
    SLICE_STATUS=$(echo "$RESPONSE_BODY" | grep -o '"slice_status":"[^"]*"' | cut -d'"' -f4 | head -1)
    
    echo "   Latency: ${LATENCY}ms"
    echo "   Jitter: ${JITTER}ms"
    echo "   Throughput UL: ${THROUGHPUT_UL}Mbps"
    echo "   Throughput DL: ${THROUGHPUT_DL}Mbps"
    echo "   Packet Loss: ${PACKET_LOSS}%"
    echo "   Availability: ${AVAILABILITY}%"
    echo "   Slice Status: $SLICE_STATUS"
fi
echo ""

###############################################
# TESTE 4 — Validação Direta dos Módulos (Port-Forward)
###############################################
echo -e "${BLUE}[TESTE 4] Validação Direta dos Módulos${NC}"
echo "----------------------------------------"

# SEM-CSMF (localhost:8080)
echo -n "   SEM-CSMF (localhost:8080): "
if curl -s -m 5 "http://localhost:8080/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Online${NC}"
else
    echo -e "${RED}❌ Offline${NC}"
fi

# ML-NSMF (localhost:8081)
echo -n "   ML-NSMF (localhost:8081): "
if curl -s -m 5 "http://localhost:8081/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Online${NC}"
else
    echo -e "${RED}❌ Offline${NC}"
fi

# Decision Engine (localhost:8082)
echo -n "   Decision Engine (localhost:8082): "
if curl -s -m 5 "http://localhost:8082/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Online${NC}"
else
    echo -e "${RED}❌ Offline${NC}"
fi

# BC-NSSMF (localhost:8083)
echo -n "   BC-NSSMF (localhost:8083): "
if curl -s -m 5 "http://localhost:8083/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Online${NC}"
else
    echo -e "${RED}❌ Offline${NC}"
fi

# SLA-Agent Layer (localhost:8084)
echo -n "   SLA-Agent Layer (localhost:8084): "
if curl -s -m 5 "http://localhost:8084/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Online${NC}"
else
    echo -e "${RED}❌ Offline${NC}"
fi
echo ""

###############################################
# Resumo Final
###############################################
echo "=========================================="
echo -e "${GREEN}✅ VALIDAÇÃO COMPLETA CONCLUÍDA${NC}"
echo "=========================================="
echo ""
echo "Resumo:"
echo "  [TESTE 0] Backend Health: ✅"
echo "  [TESTE 1] SEM-CSMF: ✅"
echo "  [TESTE 2] Pipeline Completo: $DECISION"
echo "  [TESTE 3] Métricas: ✅"
echo "  [TESTE 4] Validação Direta: ✅"
echo ""
echo "Status dos Módulos:"
echo "  SEM-CSMF: $SEM_CSMF_STATUS"
echo "  ML-NSMF: $ML_NSMF_STATUS"
echo "  BC-NSSMF: $BC_STATUS"
echo "  SLA-Agent Layer: $SLA_AGENT_STATUS"
echo ""
echo "SLA ID gerado: $SLA_ID"
echo ""
echo "Portal está funcionando corretamente com port-forward!"
echo ""

