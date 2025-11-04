#!/bin/bash
# Script para iniciar túnel SSH para Prometheus
# Uso: ./scripts-wsl/start-ssh-tunnel.sh

set -e

echo "🚇 Iniciando túnel SSH para Prometheus..."

# Verificar se já existe um túnel
if pgrep -f "ssh.*9090.*prometheus" > /dev/null; then
    TUNNEL_PID=$(pgrep -f "ssh.*9090.*prometheus" | head -1)
    echo "⚠️  Túnel SSH já está rodando (PID: $TUNNEL_PID)"
    echo "   Para parar: kill $TUNNEL_PID"
    exit 0
fi

# Configurações
JUMP_HOST="porvir5g@ppgca.unisinos.br"
TARGET_HOST="porvir5g@node006"
LOCAL_PORT=9090
REMOTE_HOST="nasp-prometheus.monitoring.svc.cluster.local"
REMOTE_PORT=9090

echo "   Jump Host: $JUMP_HOST"
echo "   Target: $TARGET_HOST"
echo "   Local Port: $LOCAL_PORT -> ${REMOTE_HOST}:${REMOTE_PORT}"
echo ""

# Iniciar túnel em background
echo "Executando túnel SSH..."
ssh -f -N -L ${LOCAL_PORT}:${REMOTE_HOST}:${REMOTE_PORT} -J $JUMP_HOST $TARGET_HOST

sleep 2

# Verificar se está rodando
if pgrep -f "ssh.*9090" > /dev/null; then
    TUNNEL_PID=$(pgrep -f "ssh.*9090" | head -1)
    echo "✅ Túnel SSH iniciado com sucesso!"
    echo "   PID: $TUNNEL_PID"
    echo "   Acesse Prometheus em: http://localhost:9090"
    echo ""
    echo "Para parar o túnel:"
    echo "   kill $TUNNEL_PID"
else
    echo "❌ Falha ao iniciar túnel SSH"
    echo "   Verifique sua conexão SSH e configuração"
    exit 1
fi





