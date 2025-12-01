#!/usr/bin/env bash
# Script simplificado de teste E2E que funciona mesmo se serviços não estiverem rodando
# Tenta criar os serviços se necessário

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TRISLA_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$TRISLA_ROOT"

echo "[TriSLA E2E Test] ==============================================="
echo "[TriSLA E2E Test] Teste de Fluxo E2E Simplificado"
echo "[TriSLA E2E Test] ==============================================="
echo ""

# Ativar venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "[TriSLA E2E Test] ❌ .venv não encontrado"
    exit 1
fi

# Verificar Besu
echo "[TriSLA E2E Test] Verificando Besu..."
BESU_OK=false
for i in {1..5}; do
    if curl -s --max-time 2 -X POST --data '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' http://127.0.0.1:8545 > /dev/null 2>&1; then
        BESU_OK=true
        echo "[TriSLA E2E Test] ✅ Besu OK"
        break
    fi
    sleep 1
done

if [ "$BESU_OK" = false ]; then
    echo "[TriSLA E2E Test] ⚠️  Besu não responde - iniciando..."
    bash scripts/blockchain/rebuild_besu.sh > /dev/null 2>&1
    sleep 10
fi

# Verificar contrato
if [ ! -f "apps/bc-nssmf/src/contracts/contract_address.json" ]; then
    echo "[TriSLA E2E Test] ⚠️  Contrato não encontrado - fazendo deploy..."
    python apps/bc-nssmf/src/deploy_contracts.py > /dev/null 2>&1
fi

# Verificar serviços Python (tentar iniciar se não estiverem rodando)
check_and_start_service() {
    local name=$1
    local port=$2
    local path=$3
    
    if curl -s --max-time 2 "http://127.0.0.1:$port/health" > /dev/null 2>&1; then
        echo "[TriSLA E2E Test] ✅ $name já está rodando"
        return 0
    else
        echo "[TriSLA E2E Test] ⚠️  $name não está rodando - tentando iniciar..."
        cd "$path"
        nohup python main.py > /tmp/${name,,}.log 2>&1 &
        local pid=$!
        echo "[TriSLA E2E Test]    $name iniciado (PID: $pid)"
        cd "$TRISLA_ROOT"
        sleep 5
        return 1
    fi
}

# Verificar/iniciar serviços
check_and_start_service "SEM-CSMF" "8080" "apps/sem-csmf/src"
check_and_start_service "ML-NSMF" "8081" "apps/ml-nsmf/src"
check_and_start_service "Decision Engine" "8082" "apps/decision-engine/src"

# Aguardar serviços iniciarem
echo "[TriSLA E2E Test] Aguardando serviços iniciarem (10s)..."
sleep 10

# Teste E2E simplificado
echo ""
echo "[TriSLA E2E Test] === Executando Teste E2E ==="
echo ""

INTENT_ID="e2e-test-$(date +%s)"
echo "[TriSLA E2E Test] Intent ID: $INTENT_ID"

# 1. Criar intent
echo "[TriSLA E2E Test] 1️⃣  Criando intent no SEM-CSMF..."
INTENT_RESP=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "{
        \"intent_id\": \"$INTENT_ID\",
        \"tenant_id\": \"e2e-tenant-001\",
        \"service_type\": \"URLLC\",
        \"sla_requirements\": {
            \"latency\": \"10ms\",
            \"reliability\": 0.999,
            \"throughput\": \"100Mbps\"
        }
    }" \
    http://127.0.0.1:8080/api/v1/intents 2>&1)

if echo "$INTENT_RESP" | grep -q "intent_id"; then
    echo "[TriSLA E2E Test]    ✅ Intent criado"
    NEST_ID=$(echo "$INTENT_RESP" | grep -o '"nest_id":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "")
    echo "[TriSLA E2E Test]    Resposta: $(echo "$INTENT_RESP" | head -c 200)..."
else
    echo "[TriSLA E2E Test]    ❌ Falha ao criar intent"
    echo "[TriSLA E2E Test]    Resposta: $INTENT_RESP"
    exit 1
fi

echo ""
echo "[TriSLA E2E Test] ✅ Teste E2E concluído!"
echo "[TriSLA E2E Test] Intent ID: $INTENT_ID"
if [ -n "$NEST_ID" ]; then
    echo "[TriSLA E2E Test] NEST ID: $NEST_ID"
fi

