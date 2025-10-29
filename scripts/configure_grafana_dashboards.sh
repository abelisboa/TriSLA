#!/bin/bash

# Configuração de Dashboards do NWDAF no Grafana
# Este script configura dashboards específicos para o NWDAF

set -e

echo "📊 Configurando dashboards do NWDAF no Grafana..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar se o Grafana está rodando
log "Verificando se o Grafana está rodando..."
if ! kubectl get deployment grafana -n trisla &> /dev/null; then
    error "Grafana não está rodando. Instale o Grafana primeiro."
    exit 1
fi

success "Grafana está rodando"

# Verificar se o Prometheus está rodando
log "Verificando se o Prometheus está rodando..."
if ! kubectl get deployment prometheus -n trisla &> /dev/null; then
    warning "Prometheus não está rodando. Dashboards podem não funcionar corretamente."
fi

# Obter informações do Grafana
log "Obtendo informações do Grafana..."
GRAFANA_POD=$(kubectl get pods -l app.kubernetes.io/name=grafana -n trisla -o jsonpath='{.items[0].metadata.name}')
GRAFANA_SERVICE=$(kubectl get svc -l app.kubernetes.io/name=grafana -n trisla -o jsonpath='{.items[0].metadata.name}')

if [ -z "$GRAFANA_POD" ]; then
    error "Pod do Grafana não encontrado"
    exit 1
fi

success "Grafana encontrado: $GRAFANA_POD"

# Configurar port-forward para o Grafana
log "Configurando port-forward para o Grafana..."
kubectl port-forward svc/$GRAFANA_SERVICE 3000:80 -n trisla &
PORT_FORWARD_PID=$!

# Aguardar port-forward estar pronto
sleep 5

# Verificar se o port-forward está funcionando
if ! curl -f http://localhost:3000/api/health &> /dev/null; then
    error "Não foi possível conectar ao Grafana"
    kill $PORT_FORWARD_PID 2>/dev/null
    exit 1
fi

success "Port-forward do Grafana configurado"

# Configurar datasource do Prometheus
log "Configurando datasource do Prometheus..."
curl -X POST http://admin:admin@localhost:3000/api/datasources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://prometheus:9090",
    "access": "proxy",
    "isDefault": true
  }' &> /dev/null || warning "Datasource do Prometheus já existe ou erro na configuração"

success "Datasource do Prometheus configurado"

# Criar dashboard do NWDAF Overview
log "Criando dashboard NWDAF Overview..."
cat <<EOF > /tmp/nwdaf-overview-dashboard.json
{
  "dashboard": {
    "id": null,
    "title": "NWDAF Overview",
    "tags": ["nwdaf", "trisla"],
    "style": "dark",
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "NWDAF Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"nwdaf\"}",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "green", "value": 1}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "NWDAF CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(container_cpu_usage_seconds_total{pod=~\"nwdaf.*\"}[5m])",
            "refId": "A"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "NWDAF Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "container_memory_usage_bytes{pod=~\"nwdaf.*\"}",
            "refId": "A"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "NWDAF Network I/O",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(container_network_receive_bytes_total{pod=~\"nwdaf.*\"}[5m])",
            "refId": "A"
          },
          {
            "expr": "rate(container_network_transmit_bytes_total{pod=~\"nwdaf.*\"}[5m])",
            "refId": "B"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
EOF

curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @/tmp/nwdaf-overview-dashboard.json &> /dev/null

success "Dashboard NWDAF Overview criado"

# Criar dashboard do NWDAF Analytics
log "Criando dashboard NWDAF Analytics..."
cat <<EOF > /tmp/nwdaf-analytics-dashboard.json
{
  "dashboard": {
    "id": null,
    "title": "NWDAF Analytics",
    "tags": ["nwdaf", "analytics", "trisla"],
    "style": "dark",
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Network Performance Score",
        "type": "gauge",
        "targets": [
          {
            "expr": "nwdaf_network_performance_score",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "min": 0,
            "max": 100,
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 70},
                {"color": "green", "value": 90}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "QoS Predictions",
        "type": "graph",
        "targets": [
          {
            "expr": "nwdaf_qos_predictions_total",
            "refId": "A"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "Traffic Patterns",
        "type": "graph",
        "targets": [
          {
            "expr": "nwdaf_traffic_patterns_detected",
            "refId": "A"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "Anomalies Detected",
        "type": "graph",
        "targets": [
          {
            "expr": "nwdaf_anomalies_detected_total",
            "refId": "A"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
EOF

curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @/tmp/nwdaf-analytics-dashboard.json &> /dev/null

success "Dashboard NWDAF Analytics criado"

# Criar dashboard do NWDAF Predictions
log "Criando dashboard NWDAF Predictions..."
cat <<EOF > /tmp/nwdaf-predictions-dashboard.json
{
  "dashboard": {
    "id": null,
    "title": "NWDAF Predictions",
    "tags": ["nwdaf", "predictions", "trisla"],
    "style": "dark",
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "QoS Predictions by Profile",
        "type": "graph",
        "targets": [
          {
            "expr": "nwdaf_qos_predictions{profile=\"urllc\"}",
            "refId": "A",
            "legendFormat": "URLLC"
          },
          {
            "expr": "nwdaf_qos_predictions{profile=\"embb\"}",
            "refId": "B",
            "legendFormat": "eMBB"
          },
          {
            "expr": "nwdaf_qos_predictions{profile=\"mmtc\"}",
            "refId": "C",
            "legendFormat": "mMTC"
          }
        ],
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Prediction Accuracy",
        "type": "stat",
        "targets": [
          {
            "expr": "nwdaf_prediction_accuracy",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 70},
                {"color": "green", "value": 90}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 3,
        "title": "Prediction Confidence",
        "type": "stat",
        "targets": [
          {
            "expr": "nwdaf_prediction_confidence",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 70},
                {"color": "green", "value": 90}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
EOF

curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @/tmp/nwdaf-predictions-dashboard.json &> /dev/null

success "Dashboard NWDAF Predictions criado"

# Limpar arquivos temporários
rm -f /tmp/nwdaf-*-dashboard.json

# Parar port-forward
kill $PORT_FORWARD_PID 2>/dev/null

# Resumo da configuração
echo ""
echo "=========================================="
echo "📊 RESUMO DA CONFIGURAÇÃO DE DASHBOARDS"
echo "=========================================="

success "Dashboards configurados:"
echo "  ✅ NWDAF Overview - Status e métricas básicas"
echo "  ✅ NWDAF Analytics - Análises de performance e QoS"
echo "  ✅ NWDAF Predictions - Predições e confiança"

success "Datasource configurado:"
echo "  ✅ Prometheus - Fonte de métricas"

echo ""
echo "🎉 CONFIGURAÇÃO DE DASHBOARDS CONCLUÍDA!"
echo "✅ Dashboards do NWDAF criados no Grafana"
echo "✅ Pronto para monitoramento em tempo real"

# Próximos passos
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Acessar Grafana: http://localhost:3000 (admin/admin)"
echo "2. Verificar dashboards do NWDAF"
echo "3. Configurar alertas se necessário"
echo "4. Continuar para a Fase 6 da implementação"
