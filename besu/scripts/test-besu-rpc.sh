#!/usr/bin/env bash
# Teste RPC BESU - TriSLA
# FASE 4: Testes automáticos

set -e

echo "🧪 [TriSLA] Testando RPC BESU..."
echo ""

# Teste eth_blockNumber
echo "1️⃣ Testando eth_blockNumber..."
RESPONSE=$(curl -s -X POST http://localhost:8545 \
    -H "Content-Type: application/json" \
    --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}')

if echo "$RESPONSE" | grep -q "result"; then
    echo "   ✅ eth_blockNumber OK: $RESPONSE"
else
    echo "   ❌ eth_blockNumber ERRO: $RESPONSE"
    exit 1
fi
echo ""

# Teste net_version
echo "2️⃣ Testando net_version..."
RESPONSE=$(curl -s -X POST http://localhost:8545 \
    -H "Content-Type: application/json" \
    --data '{"jsonrpc":"2.0","method":"net_version","params":[],"id":1}')

if echo "$RESPONSE" | grep -q "result"; then
    echo "   ✅ net_version OK: $RESPONSE"
else
    echo "   ⚠️  net_version: $RESPONSE"
fi
echo ""

# Teste admin_peers (P2P)
echo "3️⃣ Testando admin_peers (P2P)..."
RESPONSE=$(curl -s -X POST http://localhost:8545 \
    -H "Content-Type: application/json" \
    --data '{"jsonrpc":"2.0","method":"admin_peers","params":[],"id":99}')

if echo "$RESPONSE" | grep -q "result"; then
    echo "   ✅ admin_peers OK: $RESPONSE"
else
    echo "   ⚠️  admin_peers: $RESPONSE"
fi
echo ""

echo "✅ [TriSLA] Testes RPC concluídos!"

