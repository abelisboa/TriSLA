#!/usr/bin/env bash
set -e

# ========================================================================
# MASTER E2E VALIDATION - TriSLA v4.0
# Valida fluxo completo: SEM-CSMF → ML-NSMF → Decision Engine → BC-NSSMF
# ========================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TRISLA_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$TRISLA_ROOT"

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
LOG_FILE="e2e_validation.log"

echo "[TriSLA E2E] ==============================================="
echo "[TriSLA E2E] Validação E2E Completa - $TIMESTAMP"
echo "[TriSLA E2E] ==============================================="
echo ""

# ========================================================================
# Funções auxiliares
# ========================================================================

check_service() {
    local name=$1
    local url=$2
    local timeout=${3:-5}
    
    echo -n "[TriSLA E2E] Verificando $name ($url)... "
    
    if curl -s --max-time $timeout "$url" > /dev/null 2>&1; then
        echo "✅ OK"
        return 0
    else
        echo "❌ FALHOU"
        return 1
    fi
}

check_rpc() {
    echo -n "[TriSLA E2E] Verificando Besu RPC (http://127.0.0.1:8545)... "
    
    RESP=$(curl -s --max-time 5 -X POST \
        --data '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' \
        http://127.0.0.1:8545 2>/dev/null)
    
    if echo "$RESP" | grep -q "result"; then
        CHAIN_ID=$(echo "$RESP" | grep -o '"result":"[^"]*"' | cut -d'"' -f4)
        echo "✅ OK (ChainId: $CHAIN_ID)"
        return 0
    else
        echo "❌ FALHOU"
        return 1
    fi
}

# ========================================================================
# FASE 1: Validação de Serviços
# ========================================================================

echo "[TriSLA E2E] === FASE 1: Validação de Serviços ==="
echo ""

SERVICES_OK=true

# Verificar SEM-CSMF
if ! check_service "SEM-CSMF" "http://127.0.0.1:8080/health"; then
    SERVICES_OK=false
fi

# Verificar ML-NSMF
if ! check_service "ML-NSMF" "http://127.0.0.1:8081/health"; then
    SERVICES_OK=false
fi

# Verificar Decision Engine
if ! check_service "Decision Engine" "http://127.0.0.1:8082/health"; then
    SERVICES_OK=false
fi

# Verificar BC-NSSMF (se estiver rodando)
if ! check_service "BC-NSSMF" "http://127.0.0.1:8083/health" 2; then
    echo "[TriSLA E2E] ⚠️  BC-NSSMF não responde (pode estar integrado ao Decision Engine)"
fi

# Verificar Besu RPC
if ! check_rpc; then
    SERVICES_OK=false
fi

# Verificar OTLP Collector (se estiver rodando)
if docker ps --filter "name=otel-collector" --format "{{.Names}}" | grep -q otel-collector; then
    echo "[TriSLA E2E] ✅ OTLP Collector: rodando (Docker)"
else
    echo "[TriSLA E2E] ⚠️  OTLP Collector: não encontrado (opcional em DEV)"
fi

echo ""

if [ "$SERVICES_OK" = false ]; then
    echo "[TriSLA E2E] ❌ Alguns serviços não estão disponíveis."
    echo "[TriSLA E2E] Execute './TRISLA_AUTO_RUN.sh' para iniciar o pipeline completo."
    exit 1
fi

# ========================================================================
# FASE 2: Teste E2E - Fluxo Completo
# ========================================================================

echo "[TriSLA E2E] === FASE 2: Teste E2E Completo ==="
echo ""

# Gerar intent de teste
INTENT_ID="e2e-test-$(date +%s)"
INTENT_PAYLOAD=$(cat <<EOF
{
    "intent_id": "$INTENT_ID",
    "tenant_id": "e2e-tenant-001",
    "service_type": "URLLC",
    "sla_requirements": {
        "latency": "10ms",
        "reliability": 0.999,
        "throughput": "100Mbps"
    },
    "metadata": {
        "test": true,
        "e2e_validation": true
    }
}
EOF
)

echo "[TriSLA E2E] Criando intent de teste: $INTENT_ID"
echo ""

# 1. Criar intent no SEM-CSMF
echo "[TriSLA E2E] 1️⃣  Enviando intent para SEM-CSMF..."
SEM_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "$INTENT_PAYLOAD" \
    http://127.0.0.1:8080/api/v1/intents)

if echo "$SEM_RESPONSE" | grep -q "intent_id"; then
    echo "[TriSLA E2E]    ✅ Intent criado no SEM-CSMF"
    NEST_ID=$(echo "$SEM_RESPONSE" | grep -o '"nest_id":"[^"]*"' | cut -d'"' -f4 || echo "")
    if [ -n "$NEST_ID" ]; then
        echo "[TriSLA E2E]    📦 NEST ID: $NEST_ID"
    fi
else
    echo "[TriSLA E2E]    ❌ Falha ao criar intent no SEM-CSMF"
    echo "[TriSLA E2E]    Resposta: $SEM_RESPONSE"
    exit 1
fi

echo ""

# 2. Obter previsão do ML-NSMF
echo "[TriSLA E2E] 2️⃣  Obtendo previsão do ML-NSMF..."
ML_METRICS=$(cat <<EOF
{
    "latency": 10,
    "throughput": 100,
    "reliability": 0.999,
    "packet_loss": 0.001,
    "jitter": 2,
    "service_type": 2
}
EOF
)

ML_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "$ML_METRICS" \
    http://127.0.0.1:8081/api/v1/predict)

if echo "$ML_RESPONSE" | grep -q "prediction"; then
    echo "[TriSLA E2E]    ✅ Previsão obtida do ML-NSMF"
    RISK_SCORE=$(echo "$ML_RESPONSE" | grep -o '"risk_score":[0-9.]*' | cut -d':' -f2 || echo "N/A")
    RISK_LEVEL=$(echo "$ML_RESPONSE" | grep -o '"risk_level":"[^"]*"' | cut -d'"' -f4 || echo "N/A")
    echo "[TriSLA E2E]    📊 Risk Score: $RISK_SCORE | Risk Level: $RISK_LEVEL"
else
    echo "[TriSLA E2E]    ❌ Falha ao obter previsão do ML-NSMF"
    echo "[TriSLA E2E]    Resposta: $ML_RESPONSE"
    exit 1
fi

echo ""

# 3. Solicitar decisão no Decision Engine
echo "[TriSLA E2E] 3️⃣  Solicitando decisão no Decision Engine..."
DECISION_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    "http://127.0.0.1:8082/api/v1/decide/intent/$INTENT_ID?nest_id=$NEST_ID")

if echo "$DECISION_RESPONSE" | grep -q "decision_id"; then
    echo "[TriSLA E2E]    ✅ Decisão obtida do Decision Engine"
    DECISION_ACTION=$(echo "$DECISION_RESPONSE" | grep -o '"action":"[^"]*"' | cut -d'"' -f4 || echo "N/A")
    DECISION_ID=$(echo "$DECISION_RESPONSE" | grep -o '"decision_id":"[^"]*"' | cut -d'"' -f4 || echo "N/A")
    echo "[TriSLA E2E]    ⚖️  Decisão: $DECISION_ACTION | ID: $DECISION_ID"
    
    # Verificar se foi registrado no blockchain
    if echo "$DECISION_RESPONSE" | grep -q "blockchain_tx_hash"; then
        TX_HASH=$(echo "$DECISION_RESPONSE" | grep -o '"blockchain_tx_hash":"[^"]*"' | cut -d'"' -f4 || echo "")
        if [ -n "$TX_HASH" ]; then
            echo "[TriSLA E2E]    🔗 Blockchain TX: $TX_HASH"
        fi
    fi
else
    echo "[TriSLA E2E]    ❌ Falha ao obter decisão do Decision Engine"
    echo "[TriSLA E2E]    Resposta: $DECISION_RESPONSE"
    exit 1
fi

echo ""

# ========================================================================
# FASE 3: Validação Final
# ========================================================================

echo "[TriSLA E2E] === FASE 3: Validação Final ==="
echo ""

# Verificar contrato no blockchain
if [ -n "$TX_HASH" ]; then
    echo "[TriSLA E2E] ✅ SLA registrado no blockchain (TX: $TX_HASH)"
else
    echo "[TriSLA E2E] ⚠️  SLA não foi registrado no blockchain (decisão pode ter sido RENEG/REJ)"
fi

# Verificar contratos deployados
if [ -f "apps/bc-nssmf/src/contracts/contract_address.json" ]; then
    CONTRACT_ADDR=$(cat apps/bc-nssmf/src/contracts/contract_address.json | grep -o '"address":"[^"]*"' | cut -d'"' -f4)
    echo "[TriSLA E2E] ✅ Contrato BC-NSSMF: $CONTRACT_ADDR"
else
    echo "[TriSLA E2E] ⚠️  Contrato BC-NSSMF não encontrado"
fi

echo ""
echo "[TriSLA E2E] ==============================================="
echo "[TriSLA E2E] ✅ VALIDAÇÃO E2E COMPLETA - SUCESSO!"
echo "[TriSLA E2E] ==============================================="
echo ""
echo "[TriSLA E2E] Resumo:"
echo "[TriSLA E2E]   - Intent ID: $INTENT_ID"
echo "[TriSLA E2E]   - NEST ID: $NEST_ID"
echo "[TriSLA E2E]   - Decisão: $DECISION_ACTION"
echo "[TriSLA E2E]   - Blockchain TX: ${TX_HASH:-N/A}"
echo ""

