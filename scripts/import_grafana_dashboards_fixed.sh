#!/bin/bash
# Script corrigido para importar todos os dashboards do TriSLA no Grafana

set -e

echo "=========================================="
echo "📊 Importação de Dashboards TriSLA (Corrigido)"
echo "=========================================="
echo ""

# Configurações
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
GRAFANA_USER="${GRAFANA_USER:-admin}"
GRAFANA_PASS="${GRAFANA_PASS:-TriSLA2025!}"
DASHBOARDS_DIR="${DASHBOARDS_DIR:-./grafana-dashboards}"

# Verificar se Grafana está acessível
echo "🔍 Verificando conectividade com Grafana..."
if ! curl -f -s "${GRAFANA_URL}/api/health" > /dev/null 2>&1; then
    echo "❌ Grafana não está acessível em ${GRAFANA_URL}"
    echo ""
    echo "Configure o port-forward:"
    echo "  kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80 &"
    exit 1
fi
echo "✅ Grafana está acessível"
echo ""

# Verificar se diretório existe
if [ ! -d "$DASHBOARDS_DIR" ]; then
    echo "❌ Diretório de dashboards não encontrado: $DASHBOARDS_DIR"
    exit 1
fi

# Listar arquivos explicitamente
DASHBOARDS=(
    "trisla-complete-main.json"
    "trisla-slices-management.json"
    "trisla-metrics-detailed.json"
    "trisla-admin-panel.json"
    "trisla-create-slices.json"
    "trisla-centralized-view.json"
)

SUCCESS=0
FAILED=0

# Função para importar dashboard
import_dashboard() {
    local dashboard_file="$1"
    local dashboard_name=$(basename "$dashboard_file" .json)
    
    if [ ! -f "$dashboard_file" ]; then
        echo "⚠️  Dashboard não encontrado: $dashboard_file"
        return 1
    fi
    
    echo "📥 Importando: $dashboard_name..."
    
    # Preparar payload JSON completo
    RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "${GRAFANA_URL}/api/dashboards/db" \
      -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
      -H "Content-Type: application/json" \
      -d @"${dashboard_file}" 2>/dev/null)
    
    HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
    RESPONSE_BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')
    
    if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "201" ]; then
        STATUS=$(echo "$RESPONSE_BODY" | jq -r '.status // "OK"' 2>/dev/null || echo "OK")
        if [ "$STATUS" = "success" ] || echo "$RESPONSE_BODY" | grep -q "success"; then
            echo "✅ Dashboard '$dashboard_name' importado com sucesso"
            DASHBOARD_UID=$(echo "$RESPONSE_BODY" | jq -r '.uid // empty' 2>/dev/null)
            if [ ! -z "$DASHBOARD_UID" ]; then
                echo "   UID: $DASHBOARD_UID"
            fi
            return 0
        fi
    fi
    
    # Verificar se já existe (erro comum)
    if echo "$RESPONSE_BODY" | grep -qi "already exists\|duplicate"; then
        echo "ℹ️  Dashboard '$dashboard_name' já existe (atualizando)"
        # Tentar obter UID e atualizar
        DASHBOARD_UID=$(echo "$RESPONSE_BODY" | jq -r '.uid // empty' 2>/dev/null || echo "")
        if [ ! -z "$DASHBOARD_UID" ]; then
            echo "   UID: $DASHBOARD_UID"
            return 0
        fi
    fi
    
    echo "❌ Falha ao importar dashboard '$dashboard_name'"
    echo "   HTTP Status: $HTTP_STATUS"
    echo "$RESPONSE_BODY" | jq . 2>/dev/null || echo "$RESPONSE_BODY" | head -5
    return 1
}

# Importar cada dashboard
for dashboard in "${DASHBOARDS[@]}"; do
    DASHBOARD_PATH="${DASHBOARDS_DIR}/${dashboard}"
    
    if [ -f "$DASHBOARD_PATH" ]; then
        if import_dashboard "$DASHBOARD_PATH"; then
            ((SUCCESS++))
        else
            ((FAILED++))
        fi
    else
        echo "⚠️  Arquivo não encontrado: $DASHBOARD_PATH"
        ((FAILED++))
    fi
    echo ""
done

# Resumo
echo "=========================================="
echo "📊 RESUMO DA IMPORTAÇÃO"
echo "=========================================="
echo "✅ Importados com sucesso: $SUCCESS"
if [ $FAILED -gt 0 ]; then
    echo "❌ Falhados: $FAILED"
fi
echo ""

# Verificar dashboards importados
echo "🔍 Verificando dashboards importados..."
DASHBOARDS_LIST=$(curl -s -X GET "${GRAFANA_URL}/api/search?query=trisla" \
  -u "${GRAFANA_USER}:${GRAFANA_PASS}" 2>/dev/null)

if [ $? -eq 0 ] && [ ! -z "$DASHBOARDS_LIST" ]; then
    echo ""
    echo "📋 Dashboards TriSLA encontrados:"
    echo "$DASHBOARDS_LIST" | jq -r '.[] | "   • \(.title) (UID: \(.uid))"' 2>/dev/null || echo "$DASHBOARDS_LIST"
else
    echo "⚠️  Não foi possível listar dashboards"
fi
echo ""

echo "🌐 Acesse o Grafana:"
echo "   ${GRAFANA_URL}"
echo "   Usuário: ${GRAFANA_USER}"
echo "   Senha: ${GRAFANA_PASS}"
echo ""

echo "📊 Dashboards disponíveis:"
echo "   - TriSLA Portal - Dashboard Principal"
echo "   - TriSLA - Gestão de Slices"
echo "   - TriSLA - Métricas Detalhadas"
echo "   - TriSLA - Painel Administrativo"
echo "   - TriSLA - Criar Slices (LNP & Templates)"
echo "   - TriSLA - Visão Centralizada"
echo ""




