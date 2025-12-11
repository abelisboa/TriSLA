#!/usr/bin/env bash
# Script para verificar status do BESU - TriSLA
# Uso: ./check_besu.sh

set -e

RPC_URL="${RPC_URL:-http://127.0.0.1:8545}"

echo "🔍 [TriSLA] Verificando status do BESU em $RPC_URL..."

# Verificar se container está rodando
if docker ps --format '{{.Names}}' | grep -q "^trisla-besu-dev$"; then
    echo "✅ [TriSLA] Container BESU está rodando"
else
    echo "❌ [TriSLA] Container BESU não está rodando"
    exit 1
fi

# Verificar RPC
echo "🔍 [TriSLA] Testando RPC HTTP..."
RESP=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}' \
    "$RPC_URL" 2>/dev/null || echo "")

if echo "$RESP" | grep -q "result"; then
    VERSION=$(echo "$RESP" | grep -o '"result":"[^"]*"' | cut -d'"' -f4)
    echo "✅ [TriSLA] RPC OK - Versão: $VERSION"
else
    echo "❌ [TriSLA] RPC não respondeu"
    exit 1
fi

# Verificar Chain ID
echo "🔍 [TriSLA] Verificando Chain ID..."
CHAIN_ID_RESP=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' \
    "$RPC_URL")

CHAIN_ID=$(echo "$CHAIN_ID_RESP" | grep -o '"result":"0x[0-9a-f]*"' | cut -d'"' -f4)
echo "📋 [TriSLA] Chain ID: $CHAIN_ID"

# Verificar contas
echo "🔍 [TriSLA] Verificando contas..."
ACCOUNTS_RESP=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_accounts","params":[],"id":1}' \
    "$RPC_URL")

ACCOUNTS=$(echo "$ACCOUNTS_RESP" | grep -o '\[.*\]' || echo "[]")
echo "📋 [TriSLA] Contas: $ACCOUNTS"

# Verificar saldo da conta padrão
DEFAULT_ACCOUNT="0x90f8bf6a479f320ead074411a4b0e7944ea8c9c1"
BALANCE_RESP=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "{\"jsonrpc\":\"2.0\",\"method\":\"eth_getBalance\",\"params\":[\"$DEFAULT_ACCOUNT\",\"latest\"],\"id\":1}" \
    "$RPC_URL")

BALANCE_HEX=$(echo "$BALANCE_RESP" | grep -o '"result":"0x[0-9a-f]*"' | cut -d'"' -f4)
if [ -n "$BALANCE_HEX" ]; then
    BALANCE_DEC=$(printf "%d" "$BALANCE_HEX" 2>/dev/null || echo "0")
    echo "💰 [TriSLA] Saldo conta padrão: $BALANCE_HEX ($BALANCE_DEC wei)"
fi

echo "✅ [TriSLA] BESU está operacional!"
