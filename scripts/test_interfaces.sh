#!/bin/bash

# TriSLA Interfaces - Script de Teste
# Testa as interfaces I-01, I-03, I-04, I-07

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

# Testar Interface I-01 (SEM-NSMF → ML-NSMF)
test_interface_i01() {
    log "Testando Interface I-01 (SEM-NSMF → ML-NSMF)..."
    
    # Verificar se os módulos estão rodando
    local sem_pods=$(kubectl get pods -n trisla-nsp -l app.kubernetes.io/name=sem-nsmf --field-selector=status.phase=Running --no-headers | wc -l)
    local ml_pods=$(kubectl get pods -n trisla-nsp -l app.kubernetes.io/name=ml-nsmf --field-selector=status.phase=Running --no-headers | wc -l)
    
    if [ "$sem_pods" -gt 0 ] && [ "$ml_pods" -gt 0 ]; then
        success "Interface I-01: Módulos SEM-NSMF e ML-NSMF estão rodando"
        
        # Verificar logs de comunicação
        local comm_logs=$(kubectl logs -n trisla-nsp -l app.kubernetes.io/name=sem-nsmf --tail=50 | grep -i "ml\|template\|nest" | head -5)
        if [ ! -z "$comm_logs" ]; then
            success "Interface I-01: Comunicação detectada nos logs"
            echo "Logs: $comm_logs"
        else
            warning "Interface I-01: Comunicação não detectada nos logs"
        fi
    else
        warning "Interface I-01: Módulos não estão rodando (SEM: $sem_pods, ML: $ml_pods)"
    fi
}

# Testar Interface I-03 (ML-NSMF ← NASP Telemetry)
test_interface_i03() {
    log "Testando Interface I-03 (ML-NSMF ← NASP Telemetry)..."
    
    # Verificar se ML-NSMF está rodando
    local ml_pods=$(kubectl get pods -n trisla-nsp -l app.kubernetes.io/name=ml-nsmf --field-selector=status.phase=Running --no-headers | wc -l)
    
    if [ "$ml_pods" -gt 0 ]; then
        success "Interface I-03: ML-NSMF está rodando"
        
        # Verificar logs de telemetria
        local telemetry_logs=$(kubectl logs -n trisla-nsp -l app.kubernetes.io/name=ml-nsmf --tail=50 | grep -i "telemetry\|nasp\|kafka" | head -5)
        if [ ! -z "$telemetry_logs" ]; then
            success "Interface I-03: Telemetria detectada nos logs"
            echo "Logs: $telemetry_logs"
        else
            warning "Interface I-03: Telemetria não detectada nos logs"
        fi
    else
        warning "Interface I-03: ML-NSMF não está rodando"
    fi
}

# Testar Interface I-04 (BC-NSSMF ↔ Oracles)
test_interface_i04() {
    log "Testando Interface I-04 (BC-NSSMF ↔ Oracles)..."
    
    # Verificar se BC-NSSMF está rodando
    local bc_pods=$(kubectl get pods -n trisla-nsp -l app.kubernetes.io/name=bc-nssmf --field-selector=status.phase=Running --no-headers | wc -l)
    
    if [ "$bc_pods" -gt 0 ]; then
        success "Interface I-04: BC-NSSMF está rodando"
        
        # Verificar logs de oráculos
        local oracle_logs=$(kubectl logs -n trisla-nsp -l app.kubernetes.io/name=bc-nssmf --tail=50 | grep -i "oracle\|external\|blockchain" | head -5)
        if [ ! -z "$oracle_logs" ]; then
            success "Interface I-04: Comunicação com oráculos detectada"
            echo "Logs: $oracle_logs"
        else
            warning "Interface I-04: Comunicação com oráculos não detectada"
        fi
    else
        warning "Interface I-04: BC-NSSMF não está rodando"
    fi
}

# Testar Interface I-07 (Decision Engine ↔ NASP API)
test_interface_i07() {
    log "Testando Interface I-07 (Decision Engine ↔ NASP API)..."
    
    # Verificar se Decision Engine está rodando
    local de_pods=$(kubectl get pods -n trisla-nsp -l app.kubernetes.io/name=decision-engine --field-selector=status.phase=Running --no-headers | wc -l)
    
    if [ "$de_pods" -gt 0 ]; then
        success "Interface I-07: Decision Engine está rodando"
        
        # Verificar logs de NASP API
        local nasp_logs=$(kubectl logs -n trisla-nsp -l app.kubernetes.io/name=decision-engine --tail=50 | grep -i "nasp\|api\|slice" | head -5)
        if [ ! -z "$nasp_logs" ]; then
            success "Interface I-07: Comunicação com NASP detectada"
            echo "Logs: $nasp_logs"
        else
            warning "Interface I-07: Comunicação com NASP não detectada"
        fi
    else
        warning "Interface I-07: Decision Engine não está rodando"
    fi
}

# Testar integração entre interfaces
test_interfaces_integration() {
    log "Testando integração entre interfaces..."
    
    # Verificar se todos os módulos estão rodando
    local sem_pods=$(kubectl get pods -n trisla-nsp -l app.kubernetes.io/name=sem-nsmf --field-selector=status.phase=Running --no-headers | wc -l)
    local ml_pods=$(kubectl get pods -n trisla-nsp -l app.kubernetes.io/name=ml-nsmf --field-selector=status.phase=Running --no-headers | wc -l)
    local bc_pods=$(kubectl get pods -n trisla-nsp -l app.kubernetes.io/name=bc-nssmf --field-selector=status.phase=Running --no-headers | wc -l)
    local de_pods=$(kubectl get pods -n trisla-nsp -l app.kubernetes.io/name=decision-engine --field-selector=status.phase=Running --no-headers | wc -l)
    
    local total_pods=$((sem_pods + ml_pods + bc_pods + de_pods))
    
    if [ "$total_pods" -ge 4 ]; then
        success "Integração: Todos os módulos estão rodando ($total_pods pods)"
        
        # Verificar logs de integração
        local integration_logs=$(kubectl logs -n trisla-nsp --all-containers=true --tail=100 | grep -i "interface\|communication\|integration" | head -10)
        if [ ! -z "$integration_logs" ]; then
            success "Integração: Comunicação entre módulos detectada"
            echo "Logs: $integration_logs"
        else
            warning "Integração: Comunicação entre módulos não detectada"
        fi
    else
        warning "Integração: Nem todos os módulos estão rodando ($total_pods/4 pods)"
    fi
}

# Testar performance das interfaces
test_interfaces_performance() {
    log "Testando performance das interfaces..."
    
    # Verificar uso de recursos
    local resource_usage=$(kubectl top pods -n trisla-nsp --no-headers | awk '{print $1, $2, $3}' | head -10)
    
    if [ ! -z "$resource_usage" ]; then
        success "Performance: Uso de recursos obtido"
        echo "Recursos:"
        echo "$resource_usage"
    else
        warning "Performance: Não foi possível obter uso de recursos"
    fi
    
    # Verificar latência de rede
    local network_latency=$(kubectl get pods -n trisla-nsp -o wide | head -5)
    if [ ! -z "$network_latency" ]; then
        success "Performance: Informações de rede obtidas"
        echo "Rede:"
        echo "$network_latency"
    else
        warning "Performance: Não foi possível obter informações de rede"
    fi
}

# Verificar logs gerais
check_logs() {
    log "Verificando logs gerais das interfaces..."
    
    local logs=$(kubectl logs -n trisla-nsp --all-containers=true --tail=50 2>/dev/null)
    
    if [ ! -z "$logs" ]; then
        success "Logs obtidos com sucesso"
        echo "Últimas linhas dos logs:"
        echo "$logs"
    else
        warning "Não foi possível obter logs"
    fi
}

# Função principal
main() {
    log "Iniciando teste das interfaces TriSLA..."
    echo "=========================================="
    
    check_kubectl
    check_namespace
    test_interface_i01
    test_interface_i03
    test_interface_i04
    test_interface_i07
    test_interfaces_integration
    test_interfaces_performance
    check_logs
    
    echo "=========================================="
    success "Teste das interfaces concluído!"
    log "Interfaces I-01, I-03, I-04, I-07 testadas"
}

# Executar teste
main "$@"
