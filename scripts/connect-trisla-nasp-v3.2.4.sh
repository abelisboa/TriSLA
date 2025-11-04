#!/usr/bin/env bash
# ============================================================
# Connect TriSLA NASP - TriSLA Dashboard v3.2.4
# Conecta via SSH tunnel ao ambiente NASP
# ============================================================

set -e

echo "======================================================"
echo "🚇  Conector TriSLA ↔ NASP v3.2.4"
echo "======================================================"
echo ""

# Configurações (ajustar conforme necessário)
JUMP_HOST="${JUMP_HOST:-jump-host.nasp.local}"
PROMETHEUS_PORT_REMOTE="${PROMETHEUS_PORT_REMOTE:-9090}"
PROMETHEUS_PORT_LOCAL="${PROMETHEUS_PORT_LOCAL:-9092}"
SEM_NSMF_PORT_REMOTE="${SEM_NSMF_PORT_REMOTE:-8080}"
SEM_NSMF_PORT_LOCAL="${SEM_NSMF_PORT_LOCAL:-8090}"

# Verificar se SSH está disponível
if ! command -v ssh &> /dev/null; then
    echo "❌ SSH não está instalado"
    exit 1
fi

echo "📡 Configurando túneis SSH..."
echo ""

# Prometheus Tunnel
if ! pgrep -f "ssh.*${PROMETHEUS_PORT_LOCAL}:.*${PROMETHEUS_PORT_REMOTE}" > /dev/null; then
    echo "🔗 Criando túnel Prometheus: ${PROMETHEUS_PORT_REMOTE} → ${PROMETHEUS_PORT_LOCAL}"
    ssh -f -N -L ${PROMETHEUS_PORT_LOCAL}:localhost:${PROMETHEUS_PORT_REMOTE} ${JUMP_HOST} 2>/dev/null || {
        echo "⚠️  Túnel Prometheus pode já estar ativo ou erro na conexão"
    }
else
    echo "✅ Túnel Prometheus já está ativo"
fi

# SEM-NSMF Tunnel
if ! pgrep -f "ssh.*${SEM_NSMF_PORT_LOCAL}:.*${SEM_NSMF_PORT_REMOTE}" > /dev/null; then
    echo "🔗 Criando túnel SEM-NSMF: ${SEM_NSMF_PORT_REMOTE} → ${SEM_NSMF_PORT_LOCAL}"
    ssh -f -N -L ${SEM_NSMF_PORT_LOCAL}:localhost:${SEM_NSMF_PORT_REMOTE} ${JUMP_HOST} 2>/dev/null || {
        echo "⚠️  Túnel SEM-NSMF pode já estar ativo ou erro na conexão"
    }
else
    echo "✅ Túnel SEM-NSMF já está ativo"
fi

echo ""
echo "✅ SSH jump host configurado"
echo "🧩 Prometheus: porta remota ${PROMETHEUS_PORT_REMOTE} → local ${PROMETHEUS_PORT_LOCAL}"
echo "🧩 SEM-NSMF: porta remota ${SEM_NSMF_PORT_REMOTE} → local ${SEM_NSMF_PORT_LOCAL}"
echo ""

# Testar conectividade
sleep 2

if curl -s -o /dev/null -w "%{http_code}" http://localhost:${PROMETHEUS_PORT_LOCAL}/api/v1/status 2>/dev/null | grep -q "200"; then
    echo "🟢 Prometheus online"
else
    echo "⚠️  Prometheus pode não estar acessível"
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost:${SEM_NSMF_PORT_LOCAL}/health 2>/dev/null | grep -q "200"; then
    echo "🟢 SEM-NSMF online"
else
    echo "⚠️  SEM-NSMF pode não estar acessível"
fi

echo ""
echo "✅ Conexões configuradas."
echo ""
echo "Acessos locais:"
echo "  Prometheus: http://localhost:${PROMETHEUS_PORT_LOCAL}"
echo "  SEM-NSMF:   http://localhost:${SEM_NSMF_PORT_LOCAL}"
echo ""
