#!/usr/bin/env bash
# Teste integração BESU + BC-NSSMF - TriSLA
# FASE T4: Teste de integração lógica

set -e

echo "🔗 [TriSLA] Teste de Integração BESU + BC-NSSMF"
echo "================================================"
echo ""

BESU_OK=false
BC_NSSMF_OK=false
INTEGRATION_OK=false

# 1. Testar BESU RPC
echo "1️⃣ Testando BESU RPC (eth_blockNumber)..."
BESU_RESPONSE=$(curl -s -X POST http://localhost:8545 \
    -H "Content-Type: application/json" \
    --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' 2>&1 || echo "ERROR")

if echo "$BESU_RESPONSE" | grep -q "result"; then
    BESU_OK=true
    echo "   ✅ BESU RPC está acessível"
    echo "   Resposta: $BESU_RESPONSE"
else
    echo "   ❌ BESU RPC não está acessível"
    echo "   Resposta: $BESU_RESPONSE"
    exit 1
fi
echo ""

# 2. Testar BC-NSSMF (opcional)
BC_NSSMF_URL="${BC_NSSMF_URL:-http://localhost:8083}"

echo "2️⃣ Testando BC-NSSMF ($BC_NSSMF_URL)..."
BC_NSSMF_RESPONSE=$(curl -s -X POST "$BC_NSSMF_URL/api/v1/register-sla" \
    -H "Content-Type: application/json" \
    --data '{"test": "besu-connectivity"}' \
    --max-time 5 2>&1 || echo "CONNECTION_ERROR")

if echo "$BC_NSSMF_RESPONSE" | grep -qE "(error|Error|ERROR|connection|refused)"; then
    echo "   ⚠️  BC-NSSMF não está rodando ou não respondeu"
    echo "   Resposta: $BC_NSSMF_RESPONSE"
    echo "   (Isso é normal se BC-NSSMF não estiver rodando localmente)"
else
    BC_NSSMF_OK=true
    echo "   ✅ BC-NSSMF respondeu"
    echo "   Resposta: $BC_NSSMF_RESPONSE"
fi
echo ""

# 3. Resumo
echo "================================================"
echo "📊 RESUMO DA INTEGRAÇÃO"
echo "================================================"
echo ""

if [ "$BESU_OK" = true ]; then
    echo "✅ BESU RPC: OK"
    INTEGRATION_OK=true
else
    echo "❌ BESU RPC: FALHOU"
    INTEGRATION_OK=false
fi

if [ "$BC_NSSMF_OK" = true ]; then
    echo "✅ BC-NSSMF: OK"
    INTEGRATION_OK=true
elif [ "$BESU_OK" = true ]; then
    echo "⚠️  BC-NSSMF: Não rodando (opcional - BESU está pronto)"
    INTEGRATION_OK=true
else
    echo "❌ BC-NSSMF: Não testado (BESU falhou)"
fi

echo ""

if [ "$INTEGRATION_OK" = true ] && [ "$BESU_OK" = true ]; then
    echo "✅ Integração: OK"
    echo ""
    echo "✅ [TriSLA] BESU está pronto para integração com BC-NSSMF!"
    exit 0
else
    echo "❌ Integração: FALHOU"
    echo ""
    echo "❌ [TriSLA] BESU não está respondendo corretamente"
    exit 1
fi

