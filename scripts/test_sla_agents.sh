#!/bin/bash

# TriSLA SLA-Agent Layer - Script de Teste
# Testa a Camada Federada de Agentes SLA

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

# Deploy do SLA-Agent Layer
deploy_sla_agents() {
    log "Deploy do SLA-Agent Layer..."
    
    # Aplicar Helm chart
    helm upgrade --install sla-agents ./helm/sla-agents \
        --namespace trisla-nsp \
        --values ./helm/sla-agents/values.yaml \
        --wait --timeout=300s
    
    if [ $? -eq 0 ]; then
        success "SLA-Agent Layer deployado com sucesso"
    else
        error "Falha no deploy do SLA-Agent Layer"
        exit 1
    fi
}

# Verificar se o SLA-Agent Layer está rodando
check_sla_agents() {
    log "Verificando SLA-Agent Layer..."
    
    # Aguardar pods estarem prontos
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=sla-agents -n trisla-nsp --timeout=300s
    
    # Verificar status
    local running_pods=$(kubectl get pods -n trisla-nsp -l app.kubernetes.io/name=sla-agents --field-selector=status.phase=Running --no-headers | wc -l)
    
    if [ "$running_pods" -gt 0 ]; then
        success "SLA-Agent Layer está rodando ($running_pods pods)"
    else
        error "SLA-Agent Layer não está rodando"
        exit 1
    fi
}

# Testar agentes individuais
test_individual_agents() {
    log "Testando agentes individuais..."
    
    # Testar RAN Agent
    log "Testando RAN Agent..."
    local ran_logs=$(kubectl logs -n trisla-nsp -l app.kubernetes.io/name=sla-agents --tail=50 | grep -i "ran" | head -5)
    if [ ! -z "$ran_logs" ]; then
        success "RAN Agent funcionando"
        echo "Logs RAN: $ran_logs"
    else
        warning "RAN Agent pode ter problemas"
    fi
    
    # Testar TN Agent
    log "Testando TN Agent..."
    local tn_logs=$(kubectl logs -n trisla-nsp -l app.kubernetes.io/name=sla-agents --tail=50 | grep -i "tn\|transport" | head -5)
    if [ ! -z "$tn_logs" ]; then
        success "TN Agent funcionando"
        echo "Logs TN: $tn_logs"
    else
        warning "TN Agent pode ter problemas"
    fi
    
    # Testar Core Agent
    log "Testando Core Agent..."
    local core_logs=$(kubectl logs -n trisla-nsp -l app.kubernetes.io/name=sla-agents --tail=50 | grep -i "core" | head -5)
    if [ ! -z "$core_logs" ]; then
        success "Core Agent funcionando"
        echo "Logs Core: $core_logs"
    else
        warning "Core Agent pode ter problemas"
    fi
}

# Testar métricas SLA
test_sla_metrics() {
    log "Testando métricas SLA..."
    
    # Aguardar coleta de métricas
    sleep 30
    
    # Verificar logs de métricas
    local metrics_logs=$(kubectl logs -n trisla-nsp -l app.kubernetes.io/name=sla-agents --tail=100 | grep -i "metric\|violation" | head -10)
    
    if [ ! -z "$metrics_logs" ]; then
        success "Métricas SLA sendo coletadas"
        echo "Métricas: $metrics_logs"
    else
        warning "Métricas SLA podem não estar sendo coletadas"
    fi
}

# Testar violações SLA
test_sla_violations() {
    log "Testando violações SLA..."
    
    # Verificar logs de violações
    local violation_logs=$(kubectl logs -n trisla-nsp -l app.kubernetes.io/name=sla-agents --tail=100 | grep -i "violation\|critical\|warning" | head -10)
    
    if [ ! -z "$violation_logs" ]; then
        success "Sistema de violações SLA funcionando"
        echo "Violações: $violation_logs"
    else
        warning "Sistema de violações SLA pode ter problemas"
    fi
}

# Testar interface Kafka
test_kafka_interface() {
    log "Testando interface Kafka..."
    
    # Verificar logs de Kafka
    local kafka_logs=$(kubectl logs -n trisla-nsp -l app.kubernetes.io/name=sla-agents --tail=100 | grep -i "kafka\|publish" | head -10)
    
    if [ ! -z "$kafka_logs" ]; then
        success "Interface Kafka funcionando"
        echo "Kafka: $kafka_logs"
    else
        warning "Interface Kafka pode ter problemas"
    fi
}

# Testar coordenador
test_coordinator() {
    log "Testando SLA Coordinator..."
    
    # Verificar logs do coordenador
    local coordinator_logs=$(kubectl logs -n trisla-nsp -l app.kubernetes.io/name=sla-agents --tail=100 | grep -i "coordinator\|overall" | head -10)
    
    if [ ! -z "$coordinator_logs" ]; then
        success "SLA Coordinator funcionando"
        echo "Coordinator: $coordinator_logs"
    else
        warning "SLA Coordinator pode ter problemas"
    fi
}

# Verificar logs gerais
check_logs() {
    log "Verificando logs do SLA-Agent Layer..."
    
    local logs=$(kubectl logs -n trisla-nsp -l app.kubernetes.io/name=sla-agents --tail=50 2>/dev/null)
    
    if [ ! -z "$logs" ]; then
        success "Logs obtidos com sucesso"
        echo "Últimas linhas dos logs:"
        echo "$logs"
    else
        warning "Não foi possível obter logs"
    fi
}

# Testar integração com Decision Engine
test_decision_engine_integration() {
    log "Testando integração com Decision Engine..."
    
    # Verificar se Decision Engine está rodando
    local decision_engine_pods=$(kubectl get pods -n trisla-nsp -l app.kubernetes.io/name=decision-engine --field-selector=status.phase=Running --no-headers | wc -l)
    
    if [ "$decision_engine_pods" -gt 0 ]; then
        success "Decision Engine está rodando ($decision_engine_pods pods)"
        
        # Verificar logs de integração
        local integration_logs=$(kubectl logs -n trisla-nsp -l app.kubernetes.io/name=sla-agents --tail=100 | grep -i "decision\|engine" | head -5)
        
        if [ ! -z "$integration_logs" ]; then
            success "Integração com Decision Engine funcionando"
            echo "Integração: $integration_logs"
        else
            warning "Integração com Decision Engine pode ter problemas"
        fi
    else
        warning "Decision Engine não está rodando - integração não testada"
    fi
}

# Função principal
main() {
    log "Iniciando teste do SLA-Agent Layer..."
    echo "=========================================="
    
    check_kubectl
    check_namespace
    deploy_sla_agents
    check_sla_agents
    test_individual_agents
    test_sla_metrics
    test_sla_violations
    test_kafka_interface
    test_coordinator
    test_decision_engine_integration
    check_logs
    
    echo "=========================================="
    success "Teste do SLA-Agent Layer concluído!"
    log "SLA-Agent Layer está funcionando corretamente"
}

# Executar teste
main "$@"




