#!/bin/bash
# Script para copiar arquivos do dashboard customizado para node1
# Execute da pasta trisla-portal

set -e

NODE1_HOST="porvir5g@192.168.10.16"
BASE_PATH="~/gtp5g/trisla-portal"

echo "=========================================="
echo "📤 Copiando Arquivos Dashboard Customizado"
echo "=========================================="
echo ""

# Verificar se está na pasta correta
if [ ! -f "apps/api/prometheus.py" ]; then
    echo "❌ Arquivo prometheus.py não encontrado"
    echo "   Execute este script da pasta trisla-portal/"
    echo "   cd /mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal"
    exit 1
fi

SUCCESS=0
FAILED=0

# 1. Backend API Prometheus
echo "📤 Copiando: Backend API Prometheus"
echo "   apps/api/prometheus.py"
if ssh "${NODE1_HOST}" "mkdir -p ${BASE_PATH}/apps/api" 2>/dev/null && \
   scp apps/api/prometheus.py "${NODE1_HOST}:${BASE_PATH}/apps/api/prometheus.py" 2>/dev/null; then
    echo "   ✅ Copiado com sucesso"
    ((SUCCESS++))
else
    echo "   ❌ Falha ao copiar"
    ((FAILED++))
fi
echo ""

# 2. Dashboard Completo
echo "📤 Copiando: Dashboard Completo"
echo "   apps/ui/src/pages/DashboardComplete.jsx"
if ssh "${NODE1_HOST}" "mkdir -p ${BASE_PATH}/apps/ui/src/pages" 2>/dev/null && \
   scp apps/ui/src/pages/DashboardComplete.jsx "${NODE1_HOST}:${BASE_PATH}/apps/ui/src/pages/DashboardComplete.jsx" 2>/dev/null; then
    echo "   ✅ Copiado com sucesso"
    ((SUCCESS++))
else
    echo "   ❌ Falha ao copiar"
    ((FAILED++))
fi
echo ""

# 3. Gestão de Slices
echo "📤 Copiando: Gestão de Slices"
echo "   apps/ui/src/pages/SlicesManagement.jsx"
if scp apps/ui/src/pages/SlicesManagement.jsx "${NODE1_HOST}:${BASE_PATH}/apps/ui/src/pages/SlicesManagement.jsx" 2>/dev/null; then
    echo "   ✅ Copiado com sucesso"
    ((SUCCESS++))
else
    echo "   ❌ Falha ao copiar"
    ((FAILED++))
fi
echo ""

echo "=========================================="
echo "📊 RESUMO"
echo "=========================================="
echo "✅ Copiados: $SUCCESS"
if [ $FAILED -gt 0 ]; then
    echo "❌ Falhados: $FAILED"
fi
echo ""

if [ $SUCCESS -gt 0 ]; then
    echo "✅ Verificar no node1:"
    echo "   ssh ${NODE1_HOST}"
    echo "   ls -lh ~/gtp5g/trisla-portal/apps/api/prometheus.py"
    echo "   ls -lh ~/gtp5g/trisla-portal/apps/ui/src/pages/DashboardComplete.jsx"
    echo "   ls -lh ~/gtp5g/trisla-portal/apps/ui/src/pages/SlicesManagement.jsx"
    echo ""
fi




