#!/usr/bin/env bash
# Teste integração BC-NSSMF - TriSLA
# FASE 4: Testes automáticos

set -e

echo "🧪 [TriSLA] Testando integração BC-NSSMF..."
echo ""

# Verificar se BC-NSSMF está rodando
BC_NSSMF_URL="${BC_NSSMF_URL:-http://localhost:8083}"

echo "1️⃣ Verificando conectividade BC-NSSMF ($BC_NSSMF_URL)..."
RESPONSE=$(curl -s -X POST "$BC_NSSMF_URL/api/v1/register-sla" \
    -H "Content-Type: application/json" \
    --data '{"test": "besu connectivity"}' 2>&1 || echo "CONNECTION_ERROR")

if echo "$RESPONSE" | grep -qE "(error|Error|ERROR|connection|refused)"; then
    echo "   ⚠️  BC-NSSMF não está rodando ou não respondeu"
    echo "   Resposta: $RESPONSE"
else
    echo "   ✅ BC-NSSMF respondeu: $RESPONSE"
fi
echo ""

# Verificar se BESU está acessível do BC-NSSMF
echo "2️⃣ Verificando se BESU está acessível..."
BESU_RPC=$(curl -s -X POST http://localhost:8545 \
    -H "Content-Type: application/json" \
    --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' 2>&1 || echo "ERROR")

if echo "$BESU_RPC" | grep -q "result"; then
    echo "   ✅ BESU RPC está acessível"
    echo "   Resposta: $BESU_RPC"
else
    echo "   ❌ BESU RPC não está acessível"
    exit 1
fi
echo ""

echo "✅ [TriSLA] Teste integração BC-NSSMF concluído!"

