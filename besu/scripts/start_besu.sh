#!/usr/bin/env bash
# Script para iniciar BESU localmente - TriSLA
# Uso: ./start_besu.sh

set -e
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BESU_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 [TriSLA] Iniciando Hyperledger Besu..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ ERRO: Docker não está instalado."
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo "❌ ERRO: Docker não está rodando. Inicie o Docker Desktop."
    exit 1
fi

# Parar container existente se houver
if docker ps -a --format '{{.Names}}' | grep -q "^trisla-besu-dev$"; then
    echo "🛑 [TriSLA] Parando container BESU existente..."
    docker stop trisla-besu-dev 2>/dev/null || true
    docker rm trisla-besu-dev 2>/dev/null || true
fi

# Iniciar BESU
echo "📦 [TriSLA] Subindo container BESU..."
cd "$BESU_DIR"

# Tentar docker compose (v2) primeiro, depois docker-compose (v1)
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    docker compose -f docker-compose-besu.yaml up -d
elif command -v docker-compose &> /dev/null; then
    docker-compose -f docker-compose-besu.yaml up -d
else
    echo "❌ ERRO: docker compose ou docker-compose não está disponível"
    exit 1
fi

# Aguardar inicialização
echo "⏳ [TriSLA] Aguardando inicialização do BESU (30s)..."
sleep 30

# Validar RPC
echo "🔍 [TriSLA] Validando RPC HTTP..."
RPC_OK=false
for i in {1..10}; do
    RESP=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}' \
        http://127.0.0.1:8545 2>/dev/null || echo "")
    
    if echo "$RESP" | grep -q "result"; then
        echo "✅ [TriSLA] BESU RPC OK - Besu online na porta 8545"
        RPC_OK=true
        break
    fi
    
    echo "⏳ [TriSLA] Esperando RPC... Tentativa $i/10"
    sleep 5
done

if [ "$RPC_OK" = false ]; then
    echo "⚠️  [TriSLA] RPC não respondeu após 10 tentativas."
    echo "📋 [TriSLA] Verifique os logs: docker logs trisla-besu-dev"
    exit 1
fi

# Verificar chain ID
echo "🔗 [TriSLA] Verificando Chain ID..."
CHAIN_ID=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' \
    http://127.0.0.1:8545 | grep -o '"result":"0x[0-9a-f]*"' | cut -d'"' -f4)

if [ "$CHAIN_ID" = "0x539" ] || [ "$CHAIN_ID" = "0x1337" ]; then
    echo "✅ [TriSLA] Chain ID: $CHAIN_ID (correto)"
else
    echo "⚠️  [TriSLA] Chain ID inesperado: $CHAIN_ID"
fi

echo "✅ [TriSLA] BESU iniciado com sucesso!"
echo "📋 [TriSLA] RPC Endpoint: http://localhost:8545"
echo "📋 [TriSLA] Logs: docker logs -f trisla-besu-dev"
