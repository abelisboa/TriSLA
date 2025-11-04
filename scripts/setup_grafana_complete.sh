#!/bin/bash
# Script Completo de Configuração do Grafana - TriSLA Portal
# Configura datasources e importa todos os dashboards

set -e

echo "=========================================="
echo "📊 Configuração Completa do Grafana"
echo "   TriSLA Portal - NASP"
echo "=========================================="
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"; }
success() { echo -e "${GREEN}✅${NC} $1"; }
error() { echo -e "${RED}❌${NC} $1"; }
warning() { echo -e "${YELLOW}⚠️${NC} $1"; }

# Configurações
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
GRAFANA_USER="${GRAFANA_USER:-admin}"
GRAFANA_PASS="${GRAFANA_PASS:-admin}"
NAMESPACE="${NAMESPACE:-monitoring}"

# Verificar se Grafana está acessível
log "Verificando conectividade com Grafana..."
if ! curl -f -s "${GRAFANA_URL}/api/health" > /dev/null 2>&1; then
    error "Grafana não está acessível em ${GRAFANA_URL}"
    echo ""
    echo "Configure o port-forward primeiro:"
    echo "  kubectl port-forward -n ${NAMESPACE} svc/grafana 3000:80 &"
    exit 1
fi
success "Grafana está acessível"

# Testar autenticação
log "Testando autenticação..."
if ! curl -f -s -u "${GRAFANA_USER}:${GRAFANA_PASS}" "${GRAFANA_URL}/api/user" > /dev/null 2>&1; then
    error "Falha na autenticação. Verifique credenciais."
    echo ""
    echo "Obter senha:"
    echo "  kubectl get secret -n ${NAMESPACE} grafana -o jsonpath='{.data.admin-password}' | base64 -d"
    exit 1
fi
success "Autenticação OK"

# Configurar Datasource Prometheus
log "Configurando datasource Prometheus..."
PROM_URL="${PROM_URL:-http://prometheus-server.monitoring.svc.cluster.local:80}"

DS_RESPONSE=$(curl -s -X POST "${GRAFANA_URL}/api/datasources" \
  -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
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
  }")

if echo "$DS_RESPONSE" | grep -q '"id"'; then
    success "Datasource Prometheus configurado"
elif echo "$DS_RESPONSE" | grep -q "already exists"; then
    warning "Datasource Prometheus já existe"
else
    error "Falha ao configurar datasource"
    echo "$DS_RESPONSE" | jq .
    exit 1
fi

# Função para importar dashboard
import_dashboard() {
    local dashboard_file="$1"
    local dashboard_name="$2"
    
    if [ ! -f "$dashboard_file" ]; then
        warning "Dashboard não encontrado: $dashboard_file"
        return 1
    fi
    
    log "Importando dashboard: $dashboard_name..."
    
    RESPONSE=$(curl -s -X POST "${GRAFANA_URL}/api/dashboards/db" \
      -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
      -H "Content-Type: application/json" \
      -d @"${dashboard_file}")
    
    if echo "$RESPONSE" | grep -q '"status":"success"'; then
        success "Dashboard '$dashboard_name' importado"
        return 0
    elif echo "$RESPONSE" | grep -q "already exists"; then
        warning "Dashboard '$dashboard_name' já existe"
        return 0
    else
        error "Falha ao importar dashboard '$dashboard_name'"
        echo "$RESPONSE" | jq . | head -20
        return 1
    fi
}

# Importar dashboards
DASHBOARDS_DIR="${DASHBOARDS_DIR:-./grafana-dashboards}"

if [ -d "$DASHBOARDS_DIR" ]; then
    log "Procurando dashboards em: $DASHBOARDS_DIR"
    
    for dashboard in "$DASHBOARDS_DIR"/*.json; do
        if [ -f "$dashboard" ]; then
            dashboard_name=$(basename "$dashboard" .json)
            import_dashboard "$dashboard" "$dashboard_name"
        fi
    done
else
    warning "Diretório de dashboards não encontrado: $DASHBOARDS_DIR"
fi

# Criar dashboard básico se não houver dashboards
log "Criando dashboard básico do TriSLA Portal..."
BASIC_DASHBOARD=$(cat <<'EOF'
{
  "dashboard": {
    "id": null,
    "title": "TriSLA Portal - Basic",
    "tags": ["trisla"],
    "timezone": "browser",
    "refresh": "30s",
    "panels": [
      {
        "id": 1,
        "title": "API Status",
        "type": "stat",
        "gridPos": {"h": 4, "w": 12, "x": 0, "y": 0},
        "targets": [
          {
            "expr": "up{job=~\"trisla.*\"}",
            "refId": "A"
          }
        ]
      },
      {
        "id": 2,
        "title": "HTTP Requests/sec",
        "type": "graph",
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 4},
        "targets": [
          {
            "expr": "rate(http_requests_total{job=~\"trisla.*\"}[5m])",
            "refId": "A"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    }
  }
}
EOF
)

echo "$BASIC_DASHBOARD" | curl -s -X POST "${GRAFANA_URL}/api/dashboards/db" \
  -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
  -H "Content-Type: application/json" \
  -d @- > /dev/null

success "Dashboard básico criado (se necessário)"

echo ""
echo "=========================================="
echo "✅ Configuração Concluída!"
echo "=========================================="
echo ""
echo "🌐 Acesse o Grafana:"
echo "   ${GRAFANA_URL}"
echo "   Usuário: ${GRAFANA_USER}"
echo "   Senha: (obtida via kubectl get secret)"
echo ""
echo "📊 Dashboards disponíveis:"
echo "   - TriSLA Portal - Overview"
echo "   - TriSLA Portal - Basic"
echo ""
echo "🔗 Próximos passos:"
echo "   1. Acessar Grafana e verificar dashboards"
echo "   2. Configurar alertas se necessário"
echo "   3. Personalizar queries conforme necessário"
echo ""




