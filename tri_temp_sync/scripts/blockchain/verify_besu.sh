#!/usr/bin/env bash
set -e
set -o pipefail

RPC_URL="http://127.0.0.1:8545"
DEV_ADDR="0x90f8bf6a479f320ead074411a4b0e7944ea8c9c1"

echo "[TriSLA] Verificando RPC em $RPC_URL…"

CHAIN_ID=$(curl -s -X POST "$RPC_URL" \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' | jq -r '.result')

echo "[TriSLA] chainId: $CHAIN_ID"

BALANCE_HEX=$(curl -s -X POST "$RPC_URL" \
  -H "Content-Type: application/json" \
  --data "{\"jsonrpc\":\"2.0\",\"method\":\"eth_getBalance\",\"params\":[\"$DEV_ADDR\",\"latest\"],\"id\":2}" | jq -r '.result')

echo "[TriSLA] saldo DEV ($DEV_ADDR): $BALANCE_HEX"
echo "[TriSLA] Verificação básica concluída."
