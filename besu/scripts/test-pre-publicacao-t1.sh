#!/usr/bin/env bash
# FASE T1 — Verificar BESU local via docker-compose
# TriSLA - Verificação Pré-Publicação

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BESU_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔍 FASE T1 — Verificar BESU local via docker-compose"
echo "====================================================="
echo ""
echo "📁 Diretório: $BESU_DIR"
echo ""

cd "$BESU_DIR"

# 1. Derrubar e recriar ambiente
echo "1️⃣ Derrubando ambiente existente..."
docker-compose -f docker-compose-besu.yaml down -v || true
echo "✅ Ambiente derrubado"
echo ""

echo "2️⃣ Criando ambiente do zero..."
docker-compose -f docker-compose-besu.yaml up -d
echo "✅ Ambiente criado"
echo ""

# 2. Aguardar inicialização
echo "3️⃣ Aguardando inicialização (30 segundos)..."
sleep 30
echo ""

# 3. Verificar status do container
echo "4️⃣ Verificando status do container..."
docker-compose -f docker-compose-besu.yaml ps
echo ""

echo "5️⃣ Últimas 80 linhas dos logs..."
docker logs trisla-besu-dev --tail 80
echo ""

# 4. Testes RPC HTTP
echo "6️⃣ Testando RPC HTTP..."
echo ""

# Teste eth_blockNumber
echo "   Teste 1: eth_blockNumber"
RESPONSE1=$(curl -s -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' || echo "ERRO_CONEXAO")

if echo "$RESPONSE1" | grep -q '"result"'; then
    echo "   ✅ eth_blockNumber OK"
    echo "   Resposta: $RESPONSE1"
    T1_ETH_BLOCK="APROVADO"
else
    echo "   ❌ eth_blockNumber FALHOU"
    echo "   Resposta: $RESPONSE1"
    T1_ETH_BLOCK="REPROVADO"
fi
echo ""

# Teste net_version
echo "   Teste 2: net_version"
RESPONSE2=$(curl -s -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"net_version","params":[],"id":67}' || echo "ERRO_CONEXAO")

if echo "$RESPONSE2" | grep -q '"result"'; then
    CHAIN_ID=$(echo "$RESPONSE2" | grep -o '"result":"[^"]*"' | cut -d'"' -f4)
    if [ "$CHAIN_ID" = "1337" ]; then
        echo "   ✅ net_version OK (Chain ID: $CHAIN_ID)"
        echo "   Resposta: $RESPONSE2"
        T1_NET_VERSION="APROVADO"
    else
        echo "   ⚠️  net_version respondeu, mas Chain ID incorreto: $CHAIN_ID (esperado: 1337)"
        T1_NET_VERSION="REPROVADO"
    fi
else
    echo "   ❌ net_version FALHOU"
    echo "   Resposta: $RESPONSE2"
    T1_NET_VERSION="REPROVADO"
fi
echo ""

# Teste web3_clientVersion
echo "   Teste 3: web3_clientVersion"
RESPONSE3=$(curl -s -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"web3_clientVersion","params":[],"id":99}' || echo "ERRO_CONEXAO")

if echo "$RESPONSE3" | grep -q '"result"'; then
    echo "   ✅ web3_clientVersion OK"
    echo "   Resposta: $RESPONSE3"
    T1_CLIENT_VERSION="APROVADO"
else
    echo "   ❌ web3_clientVersion FALHOU"
    echo "   Resposta: $RESPONSE3"
    T1_CLIENT_VERSION="REPROVADO"
fi
echo ""

# 5. Verificar logs para erros críticos
echo "7️⃣ Verificando logs para erros críticos..."
if docker logs trisla-besu-dev 2>&1 | grep -qiE "(error|fatal|exception|failed to start|unknown option)"; then
    echo "   ⚠️  Erros encontrados nos logs:"
    docker logs trisla-besu-dev 2>&1 | grep -iE "(error|fatal|exception|failed to start|unknown option)" | head -10
    T1_LOGS="REPROVADO"
else
    echo "   ✅ Nenhum erro crítico encontrado nos logs"
    T1_LOGS="APROVADO"
fi
echo ""

# 6. Resultado final T1
echo "=========================================="
echo "📋 RESULTADO FASE T1"
echo "=========================================="
echo "eth_blockNumber:     $T1_ETH_BLOCK"
echo "net_version:          $T1_NET_VERSION"
echo "web3_clientVersion:   $T1_CLIENT_VERSION"
echo "Logs sem erros:       $T1_LOGS"
echo ""

if [ "$T1_ETH_BLOCK" = "APROVADO" ] && [ "$T1_NET_VERSION" = "APROVADO" ] && [ "$T1_CLIENT_VERSION" = "APROVADO" ] && [ "$T1_LOGS" = "APROVADO" ]; then
    echo "✅ T1: APROVADO"
    echo ""
    echo "Todos os testes passaram. BESU está funcionando corretamente localmente."
    exit 0
else
    echo "❌ T1: REPROVADO"
    echo ""
    echo "Alguns testes falharam. Revise os erros acima antes de prosseguir."
    exit 1
fi
