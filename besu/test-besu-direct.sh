#!/usr/bin/env bash
# Teste direto do BESU sem docker-compose

set -e

echo "🧪 Testando BESU diretamente..."

# Parar container existente
docker stop trisla-besu-dev 2>/dev/null || true
docker rm trisla-besu-dev 2>/dev/null || true

# Remover volume
docker volume rm besu_besu-data 2>/dev/null || true

# Criar volume
docker volume create besu_besu-data

# Executar BESU diretamente
echo "🚀 Iniciando BESU..."
docker run -d \
  --name trisla-besu-dev \
  -p 8545:8545 \
  -p 8546:8546 \
  -p 30303:30303 \
  -v besu_besu-data:/opt/besu/data \
  -v "$(pwd)/genesis.json:/opt/besu/genesis.json:ro" \
  hyperledger/besu:23.10.1 \
  --data-path=/opt/besu/data \
  --genesis-file=/opt/besu/genesis.json \
  --rpc-http-enabled=true \
  --rpc-http-host=0.0.0.0 \
  --rpc-http-port=8545 \
  --rpc-http-api=ETH,NET,WEB3,ADMIN,DEBUG \
  --host-allowlist=* \
  --network=dev \
  --miner-enabled=true \
  --min-gas-price=0

echo "⏳ Aguardando inicialização..."
sleep 30

echo "🔍 Verificando logs..."
docker logs trisla-besu-dev --tail 20

echo ""
echo "🧪 Testando RPC (web3_clientVersion)..."
curl -s -X POST http://127.0.0.1:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}' || echo "ERRO"

echo ""
echo "🧪 Testando eth_blockNumber..."
BLOCK_RESPONSE=$(curl -s -X POST http://127.0.0.1:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}')
if echo "$BLOCK_RESPONSE" | grep -q "result"; then
    echo "✅ eth_blockNumber OK: $BLOCK_RESPONSE"
else
    echo "❌ eth_blockNumber ERRO: $BLOCK_RESPONSE"
fi

