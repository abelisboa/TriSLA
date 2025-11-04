#!/bin/bash
# Script para copiar arquivos do dashboard customizado para node1

set -e

echo "=========================================="
echo "📤 Copiando Arquivos Dashboard Customizado"
echo "=========================================="
echo ""

NODE1_HOST="porvir5g@192.168.10.16"
BASE_PATH="~/gtp5g/trisla-portal"

# Arquivos para copiar
files=(
  "apps/api/prometheus.py:apps/api/prometheus.py:Backend API Prometheus"
  "apps/ui/src/pages/DashboardComplete.jsx:apps/ui/src/pages/DashboardComplete.jsx:Dashboard Completo"
  "apps/ui/src/pages/SlicesManagement.jsx:apps/ui/src/pages/SlicesManagement.jsx:Gestão de Slices"
)

# Verificar se estamos na pasta correta
if [ ! -f "apps/api/prometheus.py" ]; then
    echo "⚠️  Arquivo prometheus.py não encontrado"
    echo "   Execute este script da pasta trisla-portal/"
    echo "   cd trisla-portal"
    exit 1
fi

SUCCESS=0
FAILED=0

for file_info in "${files[@]}"; do
    IFS=':' read -r local_path remote_path description <<< "$file_info"
    
    if [ -f "$local_path" ]; then
        echo "📤 Copiando: $description"
        echo "   De: $local_path"
        echo "   Para: ${NODE1_HOST}:${BASE_PATH}/${remote_path}"
        
        # Criar diretório remoto
        REMOTE_DIR=$(dirname "${BASE_PATH}/${remote_path}")
        ssh "${NODE1_HOST}" "mkdir -p ${REMOTE_DIR}" 2>/dev/null
        
        # Copiar arquivo
        if scp "$local_path" "${NODE1_HOST}:${BASE_PATH}/${remote_path}" 2>/dev/null; then
            echo "   ✅ Copiado com sucesso"
            ((SUCCESS++))
        else
            echo "   ❌ Falha ao copiar"
            ((FAILED++))
        fi
        echo ""
    else
        echo "⚠️  Arquivo não encontrado: $local_path"
        ((FAILED++))
        echo ""
    fi
done

echo "=========================================="
echo "📊 RESUMO"
echo "=========================================="
echo "✅ Copiados: $SUCCESS"
if [ $FAILED -gt 0 ]; then
    echo "❌ Falhados: $FAILED"
fi
echo ""

if [ $SUCCESS -gt 0 ]; then
    echo "✅ Próximos passos no node1:"
    echo "   1. Verificar arquivos:"
    echo "      ls -lh ~/gtp5g/trisla-portal/apps/api/prometheus.py"
    echo ""
    echo "   2. Verificar se router está integrado:"
    echo "      grep -A 3 'prometheus_router' ~/gtp5g/trisla-portal/apps/api/main.py"
    echo ""
    echo "   3. Testar API:"
    echo "      curl http://localhost:8000/prometheus/health"
    echo ""
    echo "   4. Reiniciar services se necessário"
    echo ""
fi




