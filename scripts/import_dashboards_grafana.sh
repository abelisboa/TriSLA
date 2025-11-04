#!/bin/bash
# Script corrigido para importar dashboards no Grafana

set -e

echo "=========================================="
echo "📊 Importar Dashboards TriSLA no Grafana"
echo "=========================================="
echo ""

# Configurações
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
GRAFANA_USER="${GRAFANA_USER:-admin}"
GRAFANA_PASS="${GRAFANA_PASS:-TriSLA2025!}"
DASHBOARDS_DIR="${DASHBOARDS_DIR:-./grafana-dashboards}"

# Verificar conectividade
echo "🔍 Verificando Grafana..."
if ! curl -s -f "${GRAFANA_URL}/api/health" > /dev/null 2>&1; then
    echo "❌ Grafana não está acessível em ${GRAFANA_URL}"
    exit 1
fi
echo "✅ Grafana está acessível"
echo ""

# Verificar se diretório existe
if [ ! -d "$DASHBOARDS_DIR" ]; then
    echo "⚠️  Diretório não encontrado: $DASHBOARDS_DIR"
    echo ""
    echo "💡 Os arquivos JSON dos dashboards precisam estar em:"
    echo "   $DASHBOARDS_DIR/"
    echo ""
    echo "📋 Opções:"
    echo "   1. Importar via interface web (mais fácil):"
    echo "      - Acessar: ${GRAFANA_URL}"
    echo "      - Login: ${GRAFANA_USER} / ${GRAFANA_PASS}"
    echo "      - Ir em: Dashboards > Import > Paste JSON"
    echo ""
    echo "   2. Criar diretório e arquivos:"
    echo "      mkdir -p $DASHBOARDS_DIR"
    echo "      # Copiar arquivos JSON para lá"
    exit 1
fi

# Verificar se há arquivos JSON
DASHBOARD_FILES=($(find "$DASHBOARDS_DIR" -name "*.json" -type f 2>/dev/null))

if [ ${#DASHBOARD_FILES[@]} -eq 0 ]; then
    echo "⚠️  Nenhum arquivo JSON encontrado em $DASHBOARDS_DIR"
    echo ""
    echo "💡 Importar via interface web:"
    echo "   1. Acessar: ${GRAFANA_URL}"
    echo "   2. Login: ${GRAFANA_USER} / ${GRAFANA_PASS}"
    echo "   3. Dashboards > Import > Paste JSON"
    exit 1
fi

echo "📁 Dashboards encontrados: ${#DASHBOARD_FILES[@]}"
echo ""

# Importar cada dashboard
SUCCESS=0
FAILED=0

for dashboard_file in "${DASHBOARD_FILES[@]}"; do
    dashboard_name=$(basename "$dashboard_file" .json)
    
    echo "📥 Importando: $dashboard_name..."
    
    # Importar via API
    RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "${GRAFANA_URL}/api/dashboards/db" \
      -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
      -H "Content-Type: application/json" \
      -d @"${dashboard_file}" 2>/dev/null)
    
    HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
    RESPONSE_BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')
    
    if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "201" ]; then
        STATUS=$(echo "$RESPONSE_BODY" | jq -r '.status // "OK"' 2>/dev/null || echo "OK")
        if [ "$STATUS" = "success" ] || echo "$RESPONSE_BODY" | grep -q "success"; then
            echo "✅ Dashboard '$dashboard_name' importado"
            ((SUCCESS++))
        else
            if echo "$RESPONSE_BODY" | grep -qi "already exists\|duplicate"; then
                echo "ℹ️  Dashboard '$dashboard_name' já existe"
                ((SUCCESS++))
            else
                echo "⚠️  Importação pode ter falhado: $STATUS"
                ((FAILED++))
            fi
        fi
    else
        if echo "$RESPONSE_BODY" | grep -qi "already exists\|duplicate"; then
            echo "ℹ️  Dashboard '$dashboard_name' já existe"
            ((SUCCESS++))
        else
            echo "❌ Falha ao importar '$dashboard_name' (HTTP: $HTTP_STATUS)"
            echo "$RESPONSE_BODY" | jq . 2>/dev/null | head -5 || echo "$RESPONSE_BODY" | head -5
            ((FAILED++))
        fi
    fi
    echo ""
done

# Resumo
echo "=========================================="
echo "📊 RESUMO"
echo "=========================================="
echo "✅ Importados: $SUCCESS"
if [ $FAILED -gt 0 ]; then
    echo "❌ Falhados: $FAILED"
fi
echo ""

# Listar dashboards
echo "🔍 Dashboards TriSLA no Grafana:"
curl -s -X GET "${GRAFANA_URL}/api/search?query=trisla" \
  -u "${GRAFANA_USER}:${GRAFANA_PASS}" 2>/dev/null | \
  jq -r '.[] | "   • \(.title) (UID: \(.uid))"' 2>/dev/null || echo "   (erro ao listar)"

echo ""
echo "🌐 Acesse: ${GRAFANA_URL}"
echo ""




