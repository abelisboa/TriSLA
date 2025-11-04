#!/bin/bash
# Script para importar todos os dashboards do TriSLA no Grafana

set -e

echo "=========================================="
echo "📊 Importação de Dashboards TriSLA"
echo "=========================================="
echo ""

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configurações
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
GRAFANA_USER="${GRAFANA_USER:-admin}"
GRAFANA_PASS="${GRAFANA_PASS:-TriSLA2025!}"
DASHBOARDS_DIR="${DASHBOARDS_DIR:-./grafana-dashboards}"

# Verificar se Grafana está acessível
echo -e "${BLUE}Verificando conectividade com Grafana...${NC}"
if ! curl -f -s "${GRAFANA_URL}/api/health" > /dev/null 2>&1; then
    echo "❌ Grafana não está acessível em ${GRAFANA_URL}"
    echo ""
    echo "Configure o port-forward:"
    echo "  kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80 &"
    exit 1
fi
echo -e "${GREEN}✅ Grafana está acessível${NC}"
echo ""

# Função para importar dashboard
import_dashboard() {
    local dashboard_file="$1"
    local dashboard_name=$(basename "$dashboard_file" .json)
    
    if [ ! -f "$dashboard_file" ]; then
        echo "⚠️  Dashboard não encontrado: $dashboard_file"
        return 1
    fi
    
    echo -e "${BLUE}Importando: $dashboard_name...${NC}"
    
    RESPONSE=$(curl -s -X POST "${GRAFANA_URL}/api/dashboards/db" \
      -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
      -H "Content-Type: application/json" \
      -d @"${dashboard_file}" 2>/dev/null)
    
    if echo "$RESPONSE" | grep -q '"status":"success"'; then
        echo -e "${GREEN}✅ Dashboard '$dashboard_name' importado${NC}"
        return 0
    elif echo "$RESPONSE" | grep -q "already exists"; then
        echo -e "${BLUE}ℹ️  Dashboard '$dashboard_name' já existe (atualizando)${NC}"
        # Tentar atualizar
        DASHBOARD_UID=$(echo "$RESPONSE" | jq -r '.uid // empty' 2>/dev/null)
        if [ ! -z "$DASHBOARD_UID" ]; then
            curl -s -X POST "${GRAFANA_URL}/api/dashboards/db" \
              -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
              -H "Content-Type: application/json" \
              -d @"${dashboard_file}" | jq -r '.status // "updated"' 2>/dev/null || true
        fi
        return 0
    else
        echo "❌ Falha ao importar dashboard '$dashboard_name'"
        echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE" | head -5
        return 1
    fi
}

# Listar dashboards disponíveis
if [ ! -d "$DASHBOARDS_DIR" ]; then
    echo "❌ Diretório de dashboards não encontrado: $DASHBOARDS_DIR"
    exit 1
fi

echo -e "${BLUE}Dashboards encontrados:${NC}"
ls -1 "$DASHBOARDS_DIR"/*.json 2>/dev/null | wc -l | xargs echo "Total:"
echo ""

# Importar dashboards
SUCCESS=0
FAILED=0

for dashboard in "$DASHBOARDS_DIR"/*.json; do
    if [ -f "$dashboard" ]; then
        if import_dashboard "$dashboard"; then
            ((SUCCESS++))
        else
            ((FAILED++))
        fi
        echo ""
    fi
done

# Resumo
echo "=========================================="
echo "📊 RESUMO DA IMPORTAÇÃO"
echo "=========================================="
echo -e "${GREEN}✅ Importados com sucesso: $SUCCESS${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "❌ Falhados: $FAILED"
fi
echo ""

echo "🌐 Acesse o Grafana:"
echo "   ${GRAFANA_URL}"
echo ""

echo "📊 Dashboards disponíveis:"
echo "   - TriSLA Portal - Dashboard Principal"
echo "   - TriSLA - Gestão de Slices"
echo "   - TriSLA - Métricas Detalhadas"
echo "   - TriSLA - Painel Administrativo"
echo "   - TriSLA Portal - Overview"
echo ""

echo "🔗 Próximos passos:"
echo "   1. Acessar Grafana e verificar dashboards"
echo "   2. Configurar datasource Prometheus se necessário"
echo "   3. Personalizar queries conforme necessário"
echo "   4. Configurar alertas se necessário"
echo ""




