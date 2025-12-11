#!/usr/bin/env bash
# Script para reconstruir container BESU do zero - TriSLA
# FASE 2: Reconstruir o contêiner BESU do zero

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BESU_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔄 [TriSLA] Reconstruindo container BESU do zero..."
echo ""

cd "$BESU_DIR"

# 1. Parar e remover tudo
echo "1️⃣ Parando e removendo containers/volumes..."
docker-compose -f docker-compose-besu.yaml down -v || true
docker volume rm besu_besu-data 2>/dev/null || true
echo "✅ Limpeza concluída"
echo ""

# 2. Pull da imagem
echo "2️⃣ Fazendo pull da imagem hyperledger/besu:23.10.1..."
docker-compose -f docker-compose-besu.yaml pull
echo "✅ Imagem atualizada"
echo ""

# 3. Subir container
echo "3️⃣ Subindo container BESU..."
docker-compose -f docker-compose-besu.yaml up -d
echo "✅ Container iniciado"
echo ""

# 4. Aguardar inicialização
echo "4️⃣ Aguardando inicialização (30 segundos)..."
sleep 30
echo ""

# 5. Verificar container
echo "5️⃣ Verificando status do container..."
if docker ps | grep -q trisla-besu-dev; then
    echo "✅ Container está rodando"
else
    echo "❌ Container não está rodando!"
    docker ps -a | grep besu
    exit 1
fi
echo ""

# 6. Verificar logs (sem --miner-strategy=FAST)
echo "6️⃣ Verificando logs (sem flags inválidas)..."
if docker logs trisla-besu-dev 2>&1 | grep -q "miner-strategy"; then
    echo "❌ ERRO: Flag --miner-strategy ainda presente nos logs!"
    docker logs trisla-besu-dev --tail 50
    exit 1
else
    echo "✅ Nenhuma flag inválida encontrada"
fi
echo ""

# 7. Verificar healthcheck
echo "7️⃣ Verificando healthcheck..."
HEALTH_STATUS=$(docker inspect trisla-besu-dev --format '{{.State.Health.Status}}' 2>/dev/null || echo "no-healthcheck")
if [ "$HEALTH_STATUS" != "no-healthcheck" ]; then
    echo "   Status: $HEALTH_STATUS"
    if [ "$HEALTH_STATUS" = "healthy" ]; then
        echo "✅ Healthcheck: healthy"
    else
        echo "⏳ Healthcheck: $HEALTH_STATUS (aguardando...)"
    fi
else
    echo "⚠️  Healthcheck não configurado (normal para dev)"
fi
echo ""

echo "✅ [TriSLA] Rebuild do BESU concluído!"
echo "📋 [TriSLA] Próximo passo: Testar RPC com scripts/wait-and-test-besu.sh"

