#!/bin/bash
# Configurar Grafana - Node1
# Grafana está rodando no namespace monitoring e exposto via NodePort 30000

set -e

echo "=========================================="
echo "📊 Configuração do Grafana - TriSLA Portal"
echo "=========================================="
echo ""

# Obter credenciais do Grafana
echo "🔐 Obtendo credenciais do Grafana..."
echo ""

# Tentar obter senha do secret monitoring-grafana
GRAFANA_PASSWORD=$(kubectl get secret -n monitoring monitoring-grafana -o jsonpath='{.data.admin-password}' 2>/dev/null | base64 -d 2>/dev/null)

if [ -z "$GRAFANA_PASSWORD" ]; then
    # Tentar outros secrets
    GRAFANA_PASSWORD=$(kubectl get secret -n monitoring grafana -o jsonpath='{.data.admin-password}' 2>/dev/null | base64 -d 2>/dev/null)
fi

if [ -z "$GRAFANA_PASSWORD" ]; then
    echo "⚠️  Não foi possível obter senha automaticamente."
    echo ""
    echo "Execute manualmente:"
    echo "  kubectl get secret -n monitoring monitoring-grafana -o jsonpath='{.data.admin-password}' | base64 -d"
    echo ""
    read -p "Digite a senha do Grafana (ou Enter para usar 'admin'): " GRAFANA_PASSWORD
    GRAFANA_PASSWORD=${GRAFANA_PASSWORD:-admin}
fi

echo "✅ Credenciais obtidas"
echo "   Usuário: admin"
echo "   Senha: (verifique acima ou use 'admin' como padrão)"
echo ""

# URL do Grafana (NodePort na porta 30000)
GRAFANA_URL="http://192.168.10.16:30000"
GRAFANA_USER="admin"

echo "🌐 URLs de Acesso:"
echo "   Grafana: ${GRAFANA_URL}"
echo "   Usuário: ${GRAFANA_USER}"
echo ""

# Testar conectividade
echo "🔍 Testando conectividade com Grafana..."
if curl -f -s "${GRAFANA_URL}/api/health" > /dev/null 2>&1; then
    echo "✅ Grafana está acessível"
else
    echo "❌ Grafana não está acessível em ${GRAFANA_URL}"
    echo ""
    echo "Tentando via port-forward..."
    kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80 &
    PF_PID=$!
    sleep 3
    GRAFANA_URL="http://localhost:3000"
    echo "✅ Port-forward configurado: ${GRAFANA_URL}"
    echo "   PID: ${PF_PID}"
fi

echo ""

# Configurar datasource Prometheus
echo "📊 Configurando datasource Prometheus..."
echo ""

# Descobrir URL do Prometheus
PROM_SVC=$(kubectl get svc -n monitoring -l app.kubernetes.io/name=prometheus -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -z "$PROM_SVC" ]; then
    PROM_URL="http://prometheus-server.monitoring.svc.cluster.local:80"
else
    PROM_URL="http://${PROM_SVC}.monitoring.svc.cluster.local:80"
fi

echo "   Prometheus URL: ${PROM_URL}"
echo ""

# Configurar datasource
DS_RESPONSE=$(curl -s -X POST "${GRAFANA_URL}/api/datasources" \
  -u "${GRAFANA_USER}:${GRAFANA_PASSWORD}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Prometheus\",
    \"type\": \"prometheus\",
    \"url\": \"${PROM_URL}\",
    \"access\": \"proxy\",
    \"isDefault\": true,
    \"jsonData\": {
      \"httpMethod\": \"POST\"
    }
  }" 2>/dev/null)

if echo "$DS_RESPONSE" | grep -q '"id"\|"message":"Datasource added"'; then
    echo "✅ Datasource Prometheus configurado"
elif echo "$DS_RESPONSE" | grep -q "already exists"; then
    echo "✅ Datasource Prometheus já existe"
else
    echo "⚠️  Aviso ao configurar datasource (pode já existir)"
    echo "$DS_RESPONSE" | jq . 2>/dev/null || echo "$DS_RESPONSE"
fi

echo ""
echo "=========================================="
echo "✅ Configuração Concluída!"
echo "=========================================="
echo ""
echo "🌐 Acesse o Grafana:"
echo "   ${GRAFANA_URL}"
echo "   Usuário: ${GRAFANA_USER}"
echo "   Senha: (obtida acima ou padrão 'admin')"
echo ""
echo "📊 Próximos passos:"
echo "   1. Acessar Grafana via navegador"
echo "   2. Login com credenciais"
echo "   3. Verificar datasource Prometheus"
echo "   4. Importar dashboards (via interface web ou API)"
echo ""
echo "📋 Importar dashboard via API:"
echo "   curl -X POST \"${GRAFANA_URL}/api/dashboards/db\" \\"
echo "     -u \"${GRAFANA_USER}:${GRAFANA_PASSWORD}\" \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d @grafana-dashboards/trisla-portal-overview.json"
echo ""




