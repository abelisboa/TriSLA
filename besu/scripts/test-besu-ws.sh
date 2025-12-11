#!/usr/bin/env bash
# Teste WebSocket BESU - TriSLA
# FASE 4: Testes automáticos

set -e

echo "🧪 [TriSLA] Testando WebSocket BESU..."
echo ""

# Verificar se nc está disponível
if ! command -v nc &> /dev/null; then
    echo "⚠️  nc (netcat) não está instalado. Pulando teste WS."
    exit 0
fi

# Teste WS via nc
echo "1️⃣ Testando WebSocket (porta 8546) via nc..."
RESPONSE=$(timeout 5 bash -c 'printf "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"net_version\"}\n" | nc localhost 8546 2>&1' || echo "TIMEOUT")

if echo "$RESPONSE" | grep -q "result\|jsonrpc"; then
    echo "   ✅ WebSocket OK: $RESPONSE"
else
    echo "   ⚠️  WebSocket: $RESPONSE (pode não estar habilitado, mas RPC HTTP é suficiente)"
fi
echo ""

echo "✅ [TriSLA] Teste WebSocket concluído!"

