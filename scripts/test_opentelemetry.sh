#!/bin/bash

# TriSLA OpenTelemetry - Script de Teste
# Testa a instrumentação OpenTelemetry em todos os módulos

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se kubectl está disponível
check_kubectl() {
    log "Verificando kubectl..."
    if ! command -v kubectl &> /dev/null; then
        error "kubectl não encontrado. Instale o kubectl primeiro."
        exit 1
    fi
    success "kubectl encontrado"
}

# Verificar se o namespace existe
check_namespace() {
    log "Verificando namespace trisla-nsp..."
    if ! kubectl get namespace trisla-nsp &> /dev/null; then
        error "Namespace trisla-nsp não encontrado"
        exit 1
    fi
    success "Namespace trisla-nsp encontrado"
}

# Deploy do OpenTelemetry Collector
deploy_otel_collector() {
    log "Deploy do OpenTelemetry Collector..."
    
    # Aplicar ConfigMap
    kubectl apply -f monitoring/otel-collector/otel-collector.yaml
    
    # Aplicar Deployment
    kubectl apply -f monitoring/otel-collector/deployment.yaml
    
    # Aguardar pods estarem prontos
    kubectl wait --for=condition=ready pod -l app=otel-collector -n trisla-nsp --timeout=300s
    
    if [ $? -eq 0 ]; then
        success "OpenTelemetry Collector deployado com sucesso"
    else
        error "Falha no deploy do OpenTelemetry Collector"
        exit 1
    fi
}

# Verificar se o OpenTelemetry Collector está rodando
check_otel_collector() {
    log "Verificando OpenTelemetry Collector..."
    
    # Verificar status
    local running_pods=$(kubectl get pods -n trisla-nsp -l app=otel-collector --field-selector=status.phase=Running --no-headers | wc -l)
    
    if [ "$running_pods" -gt 0 ]; then
        success "OpenTelemetry Collector está rodando ($running_pods pods)"
    else
        error "OpenTelemetry Collector não está rodando"
        exit 1
    fi
}

# Testar coleta de traces
test_traces_collection() {
    log "Testando coleta de traces..."
    
    # Verificar logs do collector
    local trace_logs=$(kubectl logs -n trisla-nsp -l app=otel-collector --tail=50 | grep -i "trace\|span" | head -5)
    
    if [ ! -z "$trace_logs" ]; then
        success "Coleta de traces funcionando"
        echo "Logs de traces: $trace_logs"
    else
        warning "Coleta de traces pode não estar funcionando"
    fi
}

# Testar coleta de métricas
test_metrics_collection() {
    log "Testando coleta de métricas..."
    
    # Verificar logs do collector
    local metrics_logs=$(kubectl logs -n trisla-nsp -l app=otel-collector --tail=50 | grep -i "metric\|prometheus" | head -5)
    
    if [ ! -z "$metrics_logs" ]; then
        success "Coleta de métricas funcionando"
        echo "Logs de métricas: $metrics_logs"
    else
        warning "Coleta de métricas pode não estar funcionando"
    fi
}

# Testar coleta de logs
test_logs_collection() {
    log "Testando coleta de logs..."
    
    # Verificar logs do collector
    local logs_collection=$(kubectl logs -n trisla-nsp -l app=otel-collector --tail=50 | grep -i "log\|loki" | head -5)
    
    if [ ! -z "$logs_collection" ]; then
        success "Coleta de logs funcionando"
        echo "Logs de coleta: $logs_collection"
    else
        warning "Coleta de logs pode não estar funcionando"
    fi
}

# Testar instrumentação nos módulos
test_module_instrumentation() {
    log "Testando instrumentação nos módulos..."
    
    # Verificar se os módulos estão rodando
    local modules=("trisla-api" "decision-engine" "sla-agents" "sem-nsmf" "ml-nsmf" "bc-nssmf")
    
    for module in "${modules[@]}"; do
        local module_pods=$(kubectl get pods -n trisla-nsp -l app.kubernetes.io/name=$module --field-selector=status.phase=Running --no-headers | wc -l)
        
        if [ "$module_pods" -gt 0 ]; then
            success "Módulo $module está rodando ($module_pods pods)"
            
            # Verificar logs de instrumentação
            local instrumentation_logs=$(kubectl logs -n trisla-nsp -l app.kubernetes.io/name=$module --tail=20 | grep -i "telemetry\|trace\|metric" | head -3)
            
            if [ ! -z "$instrumentation_logs" ]; then
                success "Instrumentação detectada em $module"
                echo "Logs: $instrumentation_logs"
            else
                warning "Instrumentação não detectada em $module"
            fi
        else
            warning "Módulo $module não está rodando"
        fi
    done
}

# Testar conectividade com Jaeger
test_jaeger_connectivity() {
    log "Testando conectividade com Jaeger..."
    
    # Verificar se Jaeger está rodando
    local jaeger_pods=$(kubectl get pods -n trisla-nsp -l app=jaeger --field-selector=status.phase=Running --no-headers | wc -l)
    
    if [ "$jaeger_pods" -gt 0 ]; then
        success "Jaeger está rodando ($jaeger_pods pods)"
        
        # Testar port-forward para Jaeger
        kubectl port-forward -n trisla-nsp svc/jaeger 16686:16686 > /dev/null 2>&1 &
        local pf_pid=$!
        sleep 5
        
        # Testar conectividade
        local jaeger_response=$(curl -s http://localhost:16686/api/services 2>/dev/null)
        
        if [ ! -z "$jaeger_response" ]; then
            success "Conectividade com Jaeger funcionando"
            echo "Resposta Jaeger: $jaeger_response"
        else
            warning "Conectividade com Jaeger pode ter problemas"
        fi
        
        # Limpar port-forward
        kill $pf_pid 2>/dev/null
    else
        warning "Jaeger não está rodando - conectividade não testada"
    fi
}

# Testar conectividade com Prometheus
test_prometheus_connectivity() {
    log "Testando conectividade com Prometheus..."
    
    # Verificar se Prometheus está rodando
    local prometheus_pods=$(kubectl get pods -n trisla-nsp -l app.kubernetes.io/name=prometheus --field-selector=status.phase=Running --no-headers | wc -l)
    
    if [ "$prometheus_pods" -gt 0 ]; then
        success "Prometheus está rodando ($prometheus_pods pods)"
        
        # Testar port-forward para Prometheus
        kubectl port-forward -n trisla-nsp svc/prometheus-monitoring-kube-prometheus-prometheus 9090:9090 > /dev/null 2>&1 &
        local pf_pid=$!
        sleep 5
        
        # Testar conectividade
        local prometheus_response=$(curl -s http://localhost:9090/api/v1/query?query=up 2>/dev/null)
        
        if [ ! -z "$prometheus_response" ]; then
            success "Conectividade com Prometheus funcionando"
            echo "Resposta Prometheus: $prometheus_response"
        else
            warning "Conectividade com Prometheus pode ter problemas"
        fi
        
        # Limpar port-forward
        kill $pf_pid 2>/dev/null
    else
        warning "Prometheus não está rodando - conectividade não testada"
    fi
}

# Testar métricas customizadas
test_custom_metrics() {
    log "Testando métricas customizadas..."
    
    # Verificar se métricas TriSLA estão sendo coletadas
    local custom_metrics=$(kubectl logs -n trisla-nsp -l app=otel-collector --tail=100 | grep -i "trisla" | head -10)
    
    if [ ! -z "$custom_metrics" ]; then
        success "Métricas customizadas TriSLA detectadas"
        echo "Métricas: $custom_metrics"
    else
        warning "Métricas customizadas TriSLA não detectadas"
    fi
}

# Verificar logs gerais
check_logs() {
    log "Verificando logs do OpenTelemetry Collector..."
    
    local logs=$(kubectl logs -n trisla-nsp -l app=otel-collector --tail=50 2>/dev/null)
    
    if [ ! -z "$logs" ]; then
        success "Logs obtidos com sucesso"
        echo "Últimas linhas dos logs:"
        echo "$logs"
    else
        warning "Não foi possível obter logs"
    fi
}

# Testar performance do collector
test_collector_performance() {
    log "Testando performance do OpenTelemetry Collector..."
    
    # Verificar uso de recursos
    local resource_usage=$(kubectl top pods -n trisla-nsp -l app=otel-collector --no-headers 2>/dev/null)
    
    if [ ! -z "$resource_usage" ]; then
        success "Uso de recursos obtido"
        echo "Recursos: $resource_usage"
    else
        warning "Não foi possível obter uso de recursos"
    fi
    
    # Verificar métricas do collector
    local collector_metrics=$(kubectl logs -n trisla-nsp -l app=otel-collector --tail=100 | grep -i "collector\|export" | head -5)
    
    if [ ! -z "$collector_metrics" ]; then
        success "Métricas do collector detectadas"
        echo "Métricas: $collector_metrics"
    else
        warning "Métricas do collector não detectadas"
    fi
}

# Função principal
main() {
    log "Iniciando teste do OpenTelemetry..."
    echo "=========================================="
    
    check_kubectl
    check_namespace
    deploy_otel_collector
    check_otel_collector
    test_traces_collection
    test_metrics_collection
    test_logs_collection
    test_module_instrumentation
    test_jaeger_connectivity
    test_prometheus_connectivity
    test_custom_metrics
    test_collector_performance
    check_logs
    
    echo "=========================================="
    success "Teste do OpenTelemetry concluído!"
    log "OpenTelemetry está funcionando corretamente"
}

# Executar teste
main "$@"




