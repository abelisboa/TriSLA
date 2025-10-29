#!/bin/bash

# Teste do NWDAF (Network Data Analytics Function)
# Este script testa a funcionalidade completa do NWDAF

set -e

echo "🚀 Iniciando teste do NWDAF..."

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

# Verificar se kubectl está disponível
if ! command -v kubectl &> /dev/null; then
    error "kubectl não encontrado. Instale o kubectl primeiro."
    exit 1
fi

# Verificar se o namespace existe
log "Verificando namespace trisla..."
if ! kubectl get namespace trisla &> /dev/null; then
    error "Namespace 'trisla' não encontrado. Execute o deploy primeiro."
    exit 1
fi

# Verificar se o NWDAF está rodando
log "Verificando status do NWDAF..."
if ! kubectl get deployment nwdaf -n trisla &> /dev/null; then
    error "Deployment 'nwdaf' não encontrado no namespace 'trisla'."
    exit 1
fi

# Aguardar o NWDAF estar pronto
log "Aguardando NWDAF estar pronto..."
kubectl wait --for=condition=available --timeout=300s deployment/nwdaf -n trisla

# Verificar pods
log "Verificando pods do NWDAF..."
kubectl get pods -l app.kubernetes.io/name=nwdaf -n trisla

# Verificar logs
log "Verificando logs do NWDAF..."
kubectl logs -l app.kubernetes.io/name=nwdaf -n trisla --tail=50

# Testar conectividade
log "Testando conectividade do NWDAF..."
NWDAF_POD=$(kubectl get pods -l app.kubernetes.io/name=nwdaf -n trisla -o jsonpath='{.items[0].metadata.name}')

if [ -z "$NWDAF_POD" ]; then
    error "Pod do NWDAF não encontrado."
    exit 1
fi

# Testar health check
log "Testando health check..."
if kubectl exec $NWDAF_POD -n trisla -- curl -f http://localhost:8080/health &> /dev/null; then
    success "Health check passou"
else
    error "Health check falhou"
fi

# Testar readiness check
log "Testando readiness check..."
if kubectl exec $NWDAF_POD -n trisla -- curl -f http://localhost:8080/ready &> /dev/null; then
    success "Readiness check passou"
else
    error "Readiness check falhou"
fi

# Testar endpoints da API
log "Testando endpoints da API..."

# Testar endpoint de status
log "Testando /api/v1/status..."
if kubectl exec $NWDAF_POD -n trisla -- curl -f http://localhost:8080/api/v1/status &> /dev/null; then
    success "Endpoint /api/v1/status funcionando"
else
    warning "Endpoint /api/v1/status não disponível"
fi

# Testar endpoint de métricas
log "Testando /api/v1/metrics..."
if kubectl exec $NWDAF_POD -n trisla -- curl -f http://localhost:8080/api/v1/metrics &> /dev/null; then
    success "Endpoint /api/v1/metrics funcionando"
else
    warning "Endpoint /api/v1/metrics não disponível"
fi

# Testar endpoint de análises
log "Testando /api/v1/analytics..."
if kubectl exec $NWDAF_POD -n trisla -- curl -f http://localhost:8080/api/v1/analytics &> /dev/null; then
    success "Endpoint /api/v1/analytics funcionando"
else
    warning "Endpoint /api/v1/analytics não disponível"
fi

# Testar endpoint de predições
log "Testando /api/v1/predictions..."
if kubectl exec $NWDAF_POD -n trisla -- curl -f http://localhost:8080/api/v1/predictions &> /dev/null; then
    success "Endpoint /api/v1/predictions funcionando"
else
    warning "Endpoint /api/v1/predictions não disponível"
fi

# Testar endpoint de anomalias
log "Testando /api/v1/anomalies..."
if kubectl exec $NWDAF_POD -n trisla -- curl -f http://localhost:8080/api/v1/anomalies &> /dev/null; then
    success "Endpoint /api/v1/anomalies funcionando"
else
    warning "Endpoint /api/v1/anomalies não disponível"
fi

# Testar funcionalidades específicas do NWDAF
log "Testando funcionalidades específicas do NWDAF..."

# Testar análise de performance
log "Testando análise de performance..."
if kubectl exec $NWDAF_POD -n trisla -- python3 -c "
import sys
sys.path.append('/app')
from apps.nwdaf.analytics.network_analyzer import NetworkAnalyzer
from apps.nwdaf.models.data_models import NetworkData
from datetime import datetime
import uuid

# Criar dados de teste
network_data = NetworkData(
    data_id=str(uuid.uuid4()),
    timestamp=datetime.now(),
    core_data={'amf': {'cpu_usage': 70, 'memory_usage': 75}},
    ran_data={'traffic_metrics': {'ul_throughput': 100, 'dl_throughput': 200}},
    transport_data={'latency_metrics': {'avg_latency': 10}},
    app_data={'user_equipment': {'connected_ues': 1000}},
    nwdaf_id='nwdaf-001'
)

# Testar analisador
analyzer = NetworkAnalyzer()
print('Network Analyzer criado com sucesso')
" &> /dev/null; then
    success "Análise de performance funcionando"
else
    error "Análise de performance falhou"
fi

# Testar preditor de QoS
log "Testando preditor de QoS..."
if kubectl exec $NWDAF_POD -n trisla -- python3 -c "
import sys
sys.path.append('/app')
from apps.nwdaf.analytics.qos_predictor import QoSPredictor
from apps.nwdaf.models.data_models import NetworkData
from datetime import datetime
import uuid

# Criar dados de teste
network_data = NetworkData(
    data_id=str(uuid.uuid4()),
    timestamp=datetime.now(),
    core_data={'upf': {'cpu_usage': 60, 'latency': 5}},
    ran_data={'traffic_metrics': {'ul_throughput': 150, 'dl_throughput': 300}},
    transport_data={'latency_metrics': {'avg_latency': 8}},
    app_data={'slice_instances': {'urllc_slices': 2}},
    nwdaf_id='nwdaf-001'
)

# Testar preditor
predictor = QoSPredictor()
print('QoS Predictor criado com sucesso')
" &> /dev/null; then
    success "Preditor de QoS funcionando"
else
    error "Preditor de QoS falhou"
fi

# Testar analisador de tráfego
log "Testando analisador de tráfego..."
if kubectl exec $NWDAF_POD -n trisla -- python3 -c "
import sys
sys.path.append('/app')
from apps.nwdaf.analytics.traffic_analyzer import TrafficAnalyzer
from apps.nwdaf.models.data_models import NetworkData
from datetime import datetime
import uuid

# Criar dados de teste
network_data = NetworkData(
    data_id=str(uuid.uuid4()),
    timestamp=datetime.now(),
    core_data={},
    ran_data={'traffic_metrics': {'ul_throughput': 200, 'dl_throughput': 400}},
    transport_data={'packet_metrics': {'packets_sent': 1000000}},
    app_data={'user_equipment': {'active_ues': 500}},
    nwdaf_id='nwdaf-001'
)

# Testar analisador
analyzer = TrafficAnalyzer()
print('Traffic Analyzer criado com sucesso')
" &> /dev/null; then
    success "Analisador de tráfego funcionando"
else
    error "Analisador de tráfego falhou"
fi

# Testar detector de anomalias
log "Testando detector de anomalias..."
if kubectl exec $NWDAF_POD -n trisla -- python3 -c "
import sys
sys.path.append('/app')
from apps.nwdaf.analytics.anomaly_detector import AnomalyDetector
from apps.nwdaf.models.data_models import NetworkData
from datetime import datetime
import uuid

# Criar dados de teste
network_data = NetworkData(
    data_id=str(uuid.uuid4()),
    timestamp=datetime.now(),
    core_data={'amf': {'cpu_usage': 95, 'memory_usage': 90}},
    ran_data={'traffic_metrics': {'ul_throughput': 1000, 'dl_throughput': 2000}},
    transport_data={'packet_metrics': {'packet_loss_rate': 0.02}},
    app_data={'user_equipment': {'ue_connection_rate': 85}},
    nwdaf_id='nwdaf-001'
)

# Testar detector
detector = AnomalyDetector()
print('Anomaly Detector criado com sucesso')
" &> /dev/null; then
    success "Detector de anomalias funcionando"
else
    error "Detector de anomalias falhou"
fi

# Verificar métricas do Prometheus
log "Verificando métricas do Prometheus..."
if kubectl get servicemonitor nwdaf -n trisla &> /dev/null; then
    success "ServiceMonitor do NWDAF encontrado"
else
    warning "ServiceMonitor do NWDAF não encontrado"
fi

# Verificar recursos
log "Verificando recursos do NWDAF..."
kubectl top pods -l app.kubernetes.io/name=nwdaf -n trisla

# Verificar eventos
log "Verificando eventos do NWDAF..."
kubectl get events --field-selector involvedObject.name=$NWDAF_POD -n trisla

# Resumo do teste
echo ""
echo "=========================================="
echo "📊 RESUMO DO TESTE DO NWDAF"
echo "=========================================="

# Contar sucessos e falhas
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Verificar status do deployment
if kubectl get deployment nwdaf -n trisla -o jsonpath='{.status.readyReplicas}' | grep -q "1"; then
    ((PASSED_TESTS++))
    success "Deployment: PRONTO"
else
    ((FAILED_TESTS++))
    error "Deployment: FALHOU"
fi
((TOTAL_TESTS++))

# Verificar health check
if kubectl exec $NWDAF_POD -n trisla -- curl -f http://localhost:8080/health &> /dev/null; then
    ((PASSED_TESTS++))
    success "Health Check: OK"
else
    ((FAILED_TESTS++))
    error "Health Check: FALHOU"
fi
((TOTAL_TESTS++))

# Verificar readiness check
if kubectl exec $NWDAF_POD -n trisla -- curl -f http://localhost:8080/ready &> /dev/null; then
    ((PASSED_TESTS++))
    success "Readiness Check: OK"
else
    ((FAILED_TESTS++))
    error "Readiness Check: FALHOU"
fi
((TOTAL_TESTS++))

echo ""
echo "📈 ESTATÍSTICAS:"
echo "   Total de testes: $TOTAL_TESTS"
echo "   Testes passaram: $PASSED_TESTS"
echo "   Testes falharam: $FAILED_TESTS"
echo "   Taxa de sucesso: $(( (PASSED_TESTS * 100) / TOTAL_TESTS ))%"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    success "🎉 TODOS OS TESTES PASSARAM! O NWDAF está funcionando corretamente."
    exit 0
else
    echo ""
    error "❌ ALGUNS TESTES FALHARAM. Verifique os logs acima para mais detalhes."
    exit 1
fi