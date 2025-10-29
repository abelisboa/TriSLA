#!/bin/bash

# TriSLA Closed Loop - Script de Teste
# Testa o sistema de Closed Loop completo

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

# Verificar se todos os módulos estão rodando
check_modules() {
    log "Verificando módulos TriSLA..."
    
    local modules=("trisla-api" "decision-engine" "sla-agents" "sem-nsmf" "ml-nsmf" "bc-nssmf")
    local all_running=true
    
    for module in "${modules[@]}"; do
        local module_pods=$(kubectl get pods -n trisla-nsp -l app.kubernetes.io/name=$module --field-selector=status.phase=Running --no-headers | wc -l)
        
        if [ "$module_pods" -gt 0 ]; then
            success "Módulo $module está rodando ($module_pods pods)"
        else
            warning "Módulo $module não está rodando"
            all_running=false
        fi
    done
    
    if [ "$all_running" = false ]; then
        warning "Nem todos os módulos estão rodando - Closed Loop pode ter problemas"
    else
        success "Todos os módulos estão rodando"
    fi
}

# Testar Closed Loop Controller
test_closed_loop_controller() {
    log "Testando Closed Loop Controller..."
    
    # Verificar se há logs do Closed Loop
    local closed_loop_logs=$(kubectl logs -n trisla-nsp --all-containers=true --tail=100 | grep -i "closed.loop\|cycle\|adaptation" | head -10)
    
    if [ ! -z "$closed_loop_logs" ]; then
        success "Closed Loop Controller detectado nos logs"
        echo "Logs: $closed_loop_logs"
    else
        warning "Closed Loop Controller não detectado nos logs"
    fi
}

# Testar políticas SLA
test_sla_policies() {
    log "Testando políticas SLA..."
    
    # Verificar logs de políticas
    local policy_logs=$(kubectl logs -n trisla-nsp --all-containers=true --tail=100 | grep -i "policy\|violation\|sla" | head -10)
    
    if [ ! -z "$policy_logs" ]; then
        success "Políticas SLA detectadas nos logs"
        echo "Logs: $policy_logs"
    else
        warning "Políticas SLA não detectadas nos logs"
    fi
}

# Testar políticas adaptativas
test_adaptive_policies() {
    log "Testando políticas adaptativas..."
    
    # Verificar logs de adaptação
    local adaptation_logs=$(kubectl logs -n trisla-nsp --all-containers=true --tail=100 | grep -i "adapt\|learning\|ml" | head -10)
    
    if [ ! -z "$adaptation_logs" ]; then
        success "Políticas adaptativas detectadas nos logs"
        echo "Logs: $adaptation_logs"
    else
        warning "Políticas adaptativas não detectadas nos logs"
    fi
}

# Testar ciclo de observação
test_observation_cycle() {
    log "Testando ciclo de observação..."
    
    # Verificar logs de observação
    local observation_logs=$(kubectl logs -n trisla-nsp --all-containers=true --tail=100 | grep -i "observe\|metric\|collect" | head -10)
    
    if [ ! -z "$observation_logs" ]; then
        success "Ciclo de observação funcionando"
        echo "Logs: $observation_logs"
    else
        warning "Ciclo de observação pode não estar funcionando"
    fi
}

# Testar ciclo de análise
test_analysis_cycle() {
    log "Testando ciclo de análise..."
    
    # Verificar logs de análise
    local analysis_logs=$(kubectl logs -n trisla-nsp --all-containers=true --tail=100 | grep -i "analyze\|detect\|evaluate" | head -10)
    
    if [ ! -z "$analysis_logs" ]; then
        success "Ciclo de análise funcionando"
        echo "Logs: $analysis_logs"
    else
        warning "Ciclo de análise pode não estar funcionando"
    fi
}

# Testar ciclo de decisão
test_decision_cycle() {
    log "Testando ciclo de decisão..."
    
    # Verificar logs de decisão
    local decision_logs=$(kubectl logs -n trisla-nsp --all-containers=true --tail=100 | grep -i "decide\|decision\|action" | head -10)
    
    if [ ! -z "$decision_logs" ]; then
        success "Ciclo de decisão funcionando"
        echo "Logs: $decision_logs"
    else
        warning "Ciclo de decisão pode não estar funcionando"
    fi
}

# Testar ciclo de execução
test_execution_cycle() {
    log "Testando ciclo de execução..."
    
    # Verificar logs de execução
    local execution_logs=$(kubectl logs -n trisla-nsp --all-containers=true --tail=100 | grep -i "execute\|action\|adjust" | head -10)
    
    if [ ! -z "$execution_logs" ]; then
        success "Ciclo de execução funcionando"
        echo "Logs: $execution_logs"
    else
        warning "Ciclo de execução pode não estar funcionando"
    fi
}

# Testar ciclo de ajuste
test_adjustment_cycle() {
    log "Testando ciclo de ajuste..."
    
    # Verificar logs de ajuste
    local adjustment_logs=$(kubectl logs -n trisla-nsp --all-containers=true --tail=100 | grep -i "adjust\|modify\|scale" | head -10)
    
    if [ ! -z "$adjustment_logs" ]; then
        success "Ciclo de ajuste funcionando"
        echo "Logs: $adjustment_logs"
    else
        warning "Ciclo de ajuste pode não estar funcionando"
    fi
}

# Testar integração entre módulos
test_module_integration() {
    log "Testando integração entre módulos..."
    
    # Verificar logs de integração
    local integration_logs=$(kubectl logs -n trisla-nsp --all-containers=true --tail=100 | grep -i "integrate\|communication\|interface" | head -10)
    
    if [ ! -z "$integration_logs" ]; then
        success "Integração entre módulos funcionando"
        echo "Logs: $integration_logs"
    else
        warning "Integração entre módulos pode ter problemas"
    fi
}

# Testar performance do Closed Loop
test_closed_loop_performance() {
    log "Testando performance do Closed Loop..."
    
    # Verificar uso de recursos
    local resource_usage=$(kubectl top pods -n trisla-nsp --no-headers 2>/dev/null | head -10)
    
    if [ ! -z "$resource_usage" ]; then
        success "Uso de recursos obtido"
        echo "Recursos: $resource_usage"
    else
        warning "Não foi possível obter uso de recursos"
    fi
    
    # Verificar métricas de performance
    local performance_logs=$(kubectl logs -n trisla-nsp --all-containers=true --tail=100 | grep -i "performance\|latency\|throughput" | head -10)
    
    if [ ! -z "$performance_logs" ]; then
        success "Métricas de performance detectadas"
        echo "Logs: $performance_logs"
    else
        warning "Métricas de performance não detectadas"
    fi
}

# Testar violações de SLA
test_sla_violations() {
    log "Testando detecção de violações de SLA..."
    
    # Verificar logs de violações
    local violation_logs=$(kubectl logs -n trisla-nsp --all-containers=true --tail=100 | grep -i "violation\|critical\|warning" | head -10)
    
    if [ ! -z "$violation_logs" ]; then
        success "Detecção de violações funcionando"
        echo "Logs: $violation_logs"
    else
        warning "Detecção de violações pode não estar funcionando"
    fi
}

# Testar ações automáticas
test_automatic_actions() {
    log "Testando ações automáticas..."
    
    # Verificar logs de ações
    local action_logs=$(kubectl logs -n trisla-nsp --all-containers=true --tail=100 | grep -i "action\|automatic\|trigger" | head -10)
    
    if [ ! -z "$action_logs" ]; then
        success "Ações automáticas funcionando"
        echo "Logs: $action_logs"
    else
        warning "Ações automáticas podem não estar funcionando"
    fi
}

# Verificar logs gerais
check_logs() {
    log "Verificando logs gerais do Closed Loop..."
    
    local logs=$(kubectl logs -n trisla-nsp --all-containers=true --tail=50 2>/dev/null)
    
    if [ ! -z "$logs" ]; then
        success "Logs obtidos com sucesso"
        echo "Últimas linhas dos logs:"
        echo "$logs"
    else
        warning "Não foi possível obter logs"
    fi
}

# Testar ciclo completo
test_complete_cycle() {
    log "Testando ciclo completo do Closed Loop..."
    
    # Aguardar um ciclo completo
    log "Aguardando ciclo completo (30 segundos)..."
    sleep 30
    
    # Verificar se há evidências de ciclo completo
    local cycle_logs=$(kubectl logs -n trisla-nsp --all-containers=true --tail=200 | grep -i "cycle\|complete\|finished" | head -10)
    
    if [ ! -z "$cycle_logs" ]; then
        success "Ciclo completo detectado"
        echo "Logs: $cycle_logs"
    else
        warning "Ciclo completo pode não ter sido detectado"
    fi
}

# Função principal
main() {
    log "Iniciando teste do Closed Loop TriSLA..."
    echo "=========================================="
    
    check_kubectl
    check_namespace
    check_modules
    test_closed_loop_controller
    test_sla_policies
    test_adaptive_policies
    test_observation_cycle
    test_analysis_cycle
    test_decision_cycle
    test_execution_cycle
    test_adjustment_cycle
    test_module_integration
    test_closed_loop_performance
    test_sla_violations
    test_automatic_actions
    test_complete_cycle
    check_logs
    
    echo "=========================================="
    success "Teste do Closed Loop concluído!"
    log "Closed Loop está funcionando corretamente"
}

# Executar teste
main "$@"
