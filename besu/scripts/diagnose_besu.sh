#!/usr/bin/env bash
# Script de diagnóstico do BESU - TriSLA

set -e

echo "🔍 [TriSLA] Diagnóstico do BESU"
echo "=================================="
echo ""

# Verificar container
echo "1️⃣ Verificando container..."
if docker ps -a | grep -q trisla-besu-dev; then
    STATUS=$(docker inspect trisla-besu-dev --format '{{.State.Status}}' 2>/dev/null || echo "unknown")
    echo "   Status: $STATUS"
    
    if [ "$STATUS" = "running" ]; then
        echo "   ✅ Container está rodando"
    else
        echo "   ❌ Container não está rodando"
        echo "   Logs:"
        docker logs trisla-besu-dev --tail 20 2>&1 | sed 's/^/      /'
        exit 1
    fi
else
    echo "   ❌ Container não existe"
    exit 1
fi
echo ""

# Verificar logs recentes
echo "2️⃣ Últimas linhas dos logs:"
docker logs trisla-besu-dev --tail 30 2>&1 | tail -20 | sed 's/^/   /'
echo ""

# Verificar portas
echo "3️⃣ Verificando portas no container..."
if docker exec trisla-besu-dev netstat -tlnp 2>/dev/null | grep -q 8545; then
    echo "   ✅ Porta 8545 está escutando"
    docker exec trisla-besu-dev netstat -tlnp 2>/dev/null | grep 8545 | sed 's/^/      /'
elif docker exec trisla-besu-dev ss -tlnp 2>/dev/null | grep -q 8545; then
    echo "   ✅ Porta 8545 está escutando"
    docker exec trisla-besu-dev ss -tlnp 2>/dev/null | grep 8545 | sed 's/^/      /'
else
    echo "   ❌ Porta 8545 NÃO está escutando"
fi
echo ""

# Testar RPC localmente (dentro do container)
echo "4️⃣ Testando RPC dentro do container..."
RPC_TEST=$(docker exec trisla-besu-dev curl -s -X POST http://localhost:8545 \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}' 2>&1 || echo "ERRO")
if echo "$RPC_TEST" | grep -q "result"; then
    echo "   ✅ RPC responde dentro do container"
    echo "$RPC_TEST" | sed 's/^/      /'
else
    echo "   ❌ RPC não responde dentro do container"
    echo "   Resposta: $RPC_TEST"
fi
echo ""

# Testar RPC externamente
echo "5️⃣ Testando RPC externamente (localhost:8545)..."
RPC_EXT=$(curl -s -X POST http://127.0.0.1:8545 \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}' 2>&1 || echo "ERRO")
if echo "$RPC_EXT" | grep -q "result"; then
    echo "   ✅ RPC responde externamente"
    echo "$RPC_EXT" | sed 's/^/      /'
else
    echo "   ❌ RPC não responde externamente"
    echo "   Resposta: $RPC_EXT"
    echo ""
    echo "   💡 Verifique se a porta 8545 está mapeada corretamente:"
    docker port trisla-besu-dev 2>&1 | sed 's/^/      /'
fi
echo ""

# Verificar processos
echo "6️⃣ Processos no container:"
docker exec trisla-besu-dev ps aux 2>&1 | head -5 | sed 's/^/   /'
echo ""

echo "=================================="
echo "🔍 Diagnóstico concluído"

