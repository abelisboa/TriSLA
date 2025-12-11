#!/usr/bin/env bash
# Script para validar integração BESU com BC-NSSMF - TriSLA
# Uso: ./validate_besu.sh

set -e

RPC_URL="${RPC_URL:-http://127.0.0.1:8545}"
BC_NSSMF_URL="${BC_NSSMF_URL:-http://localhost:8083}"

echo "🔍 [TriSLA] Validando integração BESU ↔ BC-NSSMF..."

# 1. Verificar BESU
echo "1️⃣ [TriSLA] Verificando BESU..."
if ! curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}' \
    "$RPC_URL" | grep -q "result"; then
    echo "❌ [TriSLA] BESU não está respondendo em $RPC_URL"
    exit 1
fi
echo "✅ [TriSLA] BESU OK"

# 2. Verificar BC-NSSMF
echo "2️⃣ [TriSLA] Verificando BC-NSSMF..."
if ! curl -s "$BC_NSSMF_URL/health" | grep -q "status"; then
    echo "❌ [TriSLA] BC-NSSMF não está respondendo em $BC_NSSMF_URL"
    exit 1
fi
echo "✅ [TriSLA] BC-NSSMF OK"

# 3. Verificar se BC-NSSMF está conectado ao BESU
echo "3️⃣ [TriSLA] Verificando conexão BC-NSSMF → BESU..."
HEALTH_RESP=$(curl -s "$BC_NSSMF_URL/health")
if echo "$HEALTH_RESP" | grep -q '"rpc_connected":true'; then
    echo "✅ [TriSLA] BC-NSSMF conectado ao BESU"
else
    echo "⚠️  [TriSLA] BC-NSSMF pode não estar conectado ao BESU"
    echo "📋 [TriSLA] Resposta: $HEALTH_RESP"
fi

# 4. Testar registro de SLA (se BC-NSSMF estiver habilitado)
echo "4️⃣ [TriSLA] Testando registro de SLA..."
TEST_SLA_RESP=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{
        "customer": "test-tenant",
        "serviceName": "test-sla",
        "slaHash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "slos": [
            {"name": "latency", "value": 10, "threshold": 20}
        ]
    }' \
    "$BC_NSSMF_URL/bc/register" 2>/dev/null || echo "")

if echo "$TEST_SLA_RESP" | grep -q "tx"; then
    echo "✅ [TriSLA] Registro de SLA funcionando"
    TX_HASH=$(echo "$TEST_SLA_RESP" | grep -o '"tx":"0x[^"]*"' | cut -d'"' -f4)
    echo "📋 [TriSLA] Transaction Hash: $TX_HASH"
else
    echo "⚠️  [TriSLA] Registro de SLA falhou ou BC-NSSMF em modo degraded"
    echo "📋 [TriSLA] Resposta: $TEST_SLA_RESP"
fi

echo "✅ [TriSLA] Validação concluída!"
