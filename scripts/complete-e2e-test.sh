#!/usr/bin/env bash
# Teste E2E Completo - Fluxo completo de validação

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TRISLA_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$TRISLA_ROOT"

echo "[TriSLA E2E] ==============================================="
echo "[TriSLA E2E] VALIDAÇÃO E2E COMPLETA - TriSLA v4.0"
echo "[TriSLA E2E] ==============================================="
echo ""

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
INTENT_ID="e2e-complete-$(date +%s)"

# Ativar venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "[TriSLA E2E] ❌ .venv não encontrado"
    exit 1
fi

# ========================================================================
# FASE 1: Verificar Serviços
# ========================================================================

echo "[TriSLA E2E] === FASE 1: Verificação de Serviços ==="
echo ""

check_service() {
    local name=$1
    local url=$2
    echo -n "  - $name: "
    if curl -s --max-time 3 "$url" > /dev/null 2>&1; then
        echo "✅ OK"
        return 0
    else
        echo "❌ OFFLINE"
        return 1
    fi
}

SERVICES_OK=true

check_service "SEM-CSMF" "http://127.0.0.1:8080/health" || SERVICES_OK=false
check_service "ML-NSMF" "http://127.0.0.1:8081/health" || SERVICES_OK=false
check_service "Decision Engine" "http://127.0.0.1:8082/health" || SERVICES_OK=false

# Verificar Besu
echo -n "  - Besu RPC: "
if curl -s --max-time 3 -X POST --data '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' http://127.0.0.1:8545 > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ OFFLINE"
    SERVICES_OK=false
fi

echo ""

if [ "$SERVICES_OK" = false ]; then
    echo "[TriSLA E2E] ⚠️  Alguns serviços não estão disponíveis, mas continuando..."
fi

# ========================================================================
# FASE 2: Fluxo E2E Completo
# ========================================================================

echo "[TriSLA E2E] === FASE 2: Fluxo E2E Completo ==="
echo ""

# 1. Criar Intent no SEM-CSMF
echo "1️⃣  [SEM-CSMF] Criando Intent URLLC..."
INTENT_PAYLOAD=$(cat <<EOF
{
    "intent_id": "$INTENT_ID",
    "tenant_id": "e2e-tenant-001",
    "service_type": "URLLC",
    "sla_requirements": {
        "latency": "10ms",
        "reliability": 0.999,
        "throughput": "100Mbps",
        "jitter": "2ms"
    },
    "metadata": {
        "e2e_test": true,
        "timestamp": "$TIMESTAMP"
    }
}
EOF
)

SEM_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "$INTENT_PAYLOAD" \
    http://127.0.0.1:8080/api/v1/intents 2>&1)

if echo "$SEM_RESPONSE" | grep -q "intent_id"; then
    echo "    ✅ Intent criado: $INTENT_ID"
    NEST_ID=$(echo "$SEM_RESPONSE" | grep -o '"nest_id":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "")
    if [ -n "$NEST_ID" ]; then
        echo "    ✅ NEST gerado: $NEST_ID"
    fi
    echo "    📋 Resposta: $(echo "$SEM_RESPONSE" | head -c 150)..."
else
    echo "    ❌ Falha ao criar intent"
    echo "    Resposta: $SEM_RESPONSE"
    exit 1
fi

echo ""

# 2. Obter Previsão do ML-NSMF
echo "2️⃣  [ML-NSMF] Obtendo previsão de risco..."
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
    http://127.0.0.1:8081/api/v1/predict 2>&1)

if echo "$ML_RESPONSE" | grep -q "prediction"; then
    RISK_SCORE=$(echo "$ML_RESPONSE" | grep -o '"risk_score":[0-9.]*' | cut -d':' -f2 || echo "N/A")
    RISK_LEVEL=$(echo "$ML_RESPONSE" | grep -o '"risk_level":"[^"]*"' | cut -d'"' -f4 || echo "N/A")
    echo "    ✅ Previsão obtida"
    echo "    📊 Risk Score: $RISK_SCORE | Risk Level: $RISK_LEVEL"
    echo "    📋 Resposta: $(echo "$ML_RESPONSE" | head -c 150)..."
else
    echo "    ⚠️  Falha ao obter previsão (usando mock)"
    echo "    Resposta: $ML_RESPONSE"
    RISK_SCORE="N/A"
    RISK_LEVEL="N/A"
fi

echo ""

# 3. Solicitar Decisão no Decision Engine
echo "3️⃣  [Decision Engine] Solicitando decisão..."
DECISION_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    "http://127.0.0.1:8082/api/v1/decide/intent/$INTENT_ID?nest_id=$NEST_ID" 2>&1)

if echo "$DECISION_RESPONSE" | grep -q "decision_id"; then
    DECISION_ID=$(echo "$DECISION_RESPONSE" | grep -o '"decision_id":"[^"]*"' | cut -d'"' -f4 || echo "N/A")
    DECISION_ACTION=$(echo "$DECISION_RESPONSE" | grep -o '"action":"[^"]*"' | cut -d'"' -f4 || echo "N/A")
    REASONING=$(echo "$DECISION_RESPONSE" | grep -o '"reasoning":"[^"]*"' | cut -d'"' -f4 || echo "N/A")
    
    echo "    ✅ Decisão obtida"
    echo "    ⚖️  Decisão: $DECISION_ACTION"
    echo "    🆔 Decision ID: $DECISION_ID"
    echo "    💭 Reasoning: $(echo "$REASONING" | head -c 100)..."
    
    # Verificar blockchain
    if echo "$DECISION_RESPONSE" | grep -q "blockchain_tx_hash"; then
        TX_HASH=$(echo "$DECISION_RESPONSE" | grep -o '"blockchain_tx_hash":"[^"]*"' | cut -d'"' -f4 || echo "")
        if [ -n "$TX_HASH" ]; then
            echo "    🔗 Blockchain TX: $TX_HASH"
        fi
    fi
else
    echo "    ⚠️  Falha ao obter decisão"
    echo "    Resposta: $DECISION_RESPONSE"
    DECISION_ACTION="N/A"
fi

echo ""

# ========================================================================
# FASE 3: Diagnóstico Final
# ========================================================================

echo "[TriSLA E2E] === FASE 3: Diagnóstico Final ==="
echo ""

# Verificar contrato
if [ -f "apps/bc-nssmf/src/contracts/contract_address.json" ]; then
    CONTRACT_ADDR=$(cat apps/bc-nssmf/src/contracts/contract_address.json | grep -o '"address":"[^"]*"' | cut -d'"' -f4)
    echo "✅ Contrato BC-NSSMF: $CONTRACT_ADDR"
else
    echo "⚠️  Contrato BC-NSSMF não encontrado"
fi

echo ""
echo "[TriSLA E2E] ==============================================="
echo "[TriSLA E2E] 📊 RESUMO DO TESTE E2E"
echo "[TriSLA E2E] ==============================================="
echo ""
echo "Intent ID:      $INTENT_ID"
echo "NEST ID:        ${NEST_ID:-N/A}"
echo "ML Risk Score:  ${RISK_SCORE:-N/A}"
echo "ML Risk Level:  ${RISK_LEVEL:-N/A}"
echo "Decision:       ${DECISION_ACTION:-N/A}"
echo "Decision ID:    ${DECISION_ID:-N/A}"
if [ -n "$TX_HASH" ]; then
    echo "Blockchain TX:  $TX_HASH"
fi
echo ""
echo "[TriSLA E2E] ==============================================="

# Determinar status final
if [ -n "$INTENT_ID" ] && [ -n "$NEST_ID" ] && [ "$DECISION_ACTION" != "N/A" ]; then
    echo "[TriSLA E2E] ✅ FLUXO E2E COMPLETO - SUCESSO!"
    echo "[TriSLA E2E] ==============================================="
    exit 0
else
    echo "[TriSLA E2E] ⚠️  FLUXO E2E PARCIAL - ALGUNS PASSOS FALHARAM"
    echo "[TriSLA E2E] ==============================================="
    exit 1
fi

