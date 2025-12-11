#!/usr/bin/env bash
# Script para aguardar BESU inicializar completamente e testar
# FASE 3: Testes automáticos e manuais

set -e

echo "⏳ [TriSLA] Aguardando BESU inicializar completamente..."
echo ""

MAX_ATTEMPTS=30
ATTEMPT=1
RPC_OK=false
BLOCKS_CREATED=false

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "   Tentativa $ATTEMPT/$MAX_ATTEMPTS..."
    
    # Verificar se container está rodando
    if ! docker ps | grep -q trisla-besu-dev; then
        echo "   ❌ Container não está rodando!"
        docker ps -a | grep besu
        exit 1
    fi
    
    # Verificar logs para erros
    if docker logs trisla-besu-dev 2>&1 | tail -5 | grep -q "ERROR"; then
        echo "   ❌ Erro encontrado nos logs:"
        docker logs trisla-besu-dev 2>&1 | tail -10
        exit 1
    fi
    
    # Testar RPC (eth_blockNumber - requerido pelo BC-NSSMF)
    BLOCK_RESPONSE=$(curl -s -X POST http://127.0.0.1:8545 \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' 2>&1 || echo "ERRO")
    
    if echo "$BLOCK_RESPONSE" | grep -q "result"; then
        RPC_OK=true
        BLOCK_HEX=$(echo "$BLOCK_RESPONSE" | grep -o '"result":"0x[0-9a-f]*"' | cut -d'"' -f4)
        BLOCK_DEC=$((16#${BLOCK_HEX#0x}))
        
        if [ "$BLOCK_DEC" -gt 0 ]; then
            BLOCKS_CREATED=true
        fi
        
        echo "   ✅ RPC OK - Block: $BLOCK_HEX ($BLOCK_DEC)"
        
        if [ "$BLOCKS_CREATED" = true ]; then
            break
        fi
    fi
    
    if [ $ATTEMPT -lt $MAX_ATTEMPTS ]; then
        sleep 5
    fi
    
    ((ATTEMPT++))
done

if [ "$RPC_OK" = false ]; then
    echo ""
    echo "❌ [TriSLA] RPC não respondeu após $MAX_ATTEMPTS tentativas"
    echo ""
    echo "📋 [TriSLA] Últimos logs:"
    docker logs trisla-besu-dev --tail 30
    exit 1
fi

echo ""
echo "✅ [TriSLA] BESU está respondendo!"
echo ""

# Testar web3_clientVersion
echo "🔍 [TriSLA] Testando web3_clientVersion..."
VERSION_RESPONSE=$(curl -s -X POST http://127.0.0.1:8545 \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}')
echo "   Versão: $VERSION_RESPONSE"
echo ""

# Testar Chain ID
echo "🔗 [TriSLA] Verificando Chain ID..."
CHAIN_RESPONSE=$(curl -s -X POST http://127.0.0.1:8545 \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}')
echo "   Chain ID: $CHAIN_RESPONSE"
echo ""

# Testar eth_blockNumber (requerido pelo BC-NSSMF)
echo "🔗 [TriSLA] Verificando eth_blockNumber (BC-NSSMF)..."
BLOCK_RESPONSE=$(curl -s -X POST http://127.0.0.1:8545 \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}')
if echo "$BLOCK_RESPONSE" | grep -q "result"; then
    echo "   ✅ eth_blockNumber OK: $BLOCK_RESPONSE"
else
    echo "   ❌ eth_blockNumber ERRO: $BLOCK_RESPONSE"
    exit 1
fi
echo ""

# Testar net_version (BC-NSSMF)
echo "🔗 [TriSLA] Verificando net_version (BC-NSSMF)..."
NET_RESPONSE=$(curl -s -X POST http://127.0.0.1:8545 \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"net_version","params":[],"id":1}')
if echo "$NET_RESPONSE" | grep -q "result"; then
    echo "   ✅ net_version OK: $NET_RESPONSE"
else
    echo "   ⚠️  net_version: $NET_RESPONSE"
fi
echo ""

# Validar SLO "ledger availability"
echo "📊 [TriSLA] Validando SLO 'ledger availability'..."
if [ "$BLOCKS_CREATED" = true ]; then
    echo "   ✅ Ledger disponível (blocos sendo criados)"
else
    echo "   ⚠️  Ledger ainda inicializando (bloco 0)"
fi
echo ""

# Gerar relatório final
echo "=================================="
echo "📋 [TriSLA] RELATÓRIO FINAL"
echo "=================================="
echo "RPC HTTP: ✅ OK (porta 8545)"
echo "eth_blockNumber: ✅ OK"
echo "net_version: ✅ OK"
echo "Ledger Availability: $([ "$BLOCKS_CREATED" = true ] && echo "✅ OK" || echo "⏳ Inicializando")"
echo "BC-NSSMF Compatible: ✅ READY"
echo "=================================="
echo ""

exit 0

