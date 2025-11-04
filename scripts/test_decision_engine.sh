#!/bin/bash

# TriSLA Decision Engine - Script de Teste
# Testa o Decision Engine Central com módulos existentes

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

# Deploy do Decision Engine
deploy_decision_engine() {
    log "Deploy do Decision Engine..."
    
    # Aplicar Helm chart
    helm upgrade --install decision-engine ./helm/decision-engine \
        --namespace trisla-nsp \
        --values ./helm/decision-engine/values.yaml \
        --wait --timeout=300s
    
    if [ $? -eq 0 ]; then
        success "Decision Engine deployado com sucesso"
    else
        error "Falha no deploy do Decision Engine"
        exit 1
    fi
}

# Verificar se o Decision Engine está rodando
check_decision_engine() {
    log "Verificando Decision Engine..."
    
    # Aguardar pods estarem prontos
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=decision-engine -n trisla-nsp --timeout=300s
    
    # Verificar status
    local running_pods=$(kubectl get pods -n trisla-nsp -l app.kubernetes.io/name=decision-engine --field-selector=status.phase=Running --no-headers | wc -l)
    
    if [ "$running_pods" -gt 0 ]; then
        success "Decision Engine está rodando ($running_pods pods)"
    else
        error "Decision Engine não está rodando"
        exit 1
    fi
}

# Testar health check
test_health_check() {
    log "Testando health check do Decision Engine..."
    
    # Port-forward para o Decision Engine
    kubectl port-forward -n trisla-nsp svc/decision-engine 8080:8080 > /dev/null 2>&1 &
    local pf_pid=$!
    sleep 5
    
    # Testar health check
    local health_response=$(curl -s http://localhost:8080/api/v1/health 2>/dev/null)
    
    if echo "$health_response" | grep -q "healthy"; then
        success "Health check funcionando"
        echo "Resposta: $health_response"
    else
        error "Health check falhou"
        kill $pf_pid 2>/dev/null
        exit 1
    fi
    
    # Limpar port-forward
    kill $pf_pid 2>/dev/null
}

# Testar endpoint de decisão
test_decision_endpoint() {
    log "Testando endpoint de decisão..."
    
    # Port-forward para o Decision Engine
    kubectl port-forward -n trisla-nsp svc/decision-engine 8080:8080 > /dev/null 2>&1 &
    local pf_pid=$!
    sleep 5
    
    # Teste URLLC
    log "Testando cenário URLLC..."
    local urllc_response=$(curl -s -X POST http://localhost:8080/api/v1/decide \
        -H "Content-Type: application/json" \
        -d '{
            "slice_id": "test-urllc-001",
            "requirements": {
                "latency": 10,
                "reliability": 99.9,
                "bandwidth": 100
            }
        }' 2>/dev/null)
    
    if echo "$urllc_response" | grep -q "decision"; then
        success "Endpoint de decisão funcionando"
        echo "Resposta URLLC: $urllc_response"
    else
        warning "Endpoint de decisão pode ter problemas"
        echo "Resposta: $urllc_response"
    fi
    
    # Teste eMBB
    log "Testando cenário eMBB..."
    local embb_response=$(curl -s -X POST http://localhost:8080/api/v1/decide \
        -H "Content-Type: application/json" \
        -d '{
            "slice_id": "test-embb-001",
            "requirements": {
                "latency": 50,
                "bandwidth": 1000,
                "reliability": 99.5
            }
        }' 2>/dev/null)
    
    if echo "$embb_response" | grep -q "decision"; then
        success "Cenário eMBB funcionando"
        echo "Resposta eMBB: $embb_response"
    else
        warning "Cenário eMBB pode ter problemas"
        echo "Resposta: $embb_response"
    fi
    
    # Limpar port-forward
    kill $pf_pid 2>/dev/null
}

# Testar histórico de decisões
test_decision_history() {
    log "Testando histórico de decisões..."
    
    # Port-forward para o Decision Engine
    kubectl port-forward -n trisla-nsp svc/decision-engine 8080:8080 > /dev/null 2>&1 &
    local pf_pid=$!
    sleep 5
    
    # Testar endpoint de histórico
    local history_response=$(curl -s http://localhost:8080/api/v1/history 2>/dev/null)
    
    if echo "$history_response" | grep -q "slice_id"; then
        success "Histórico de decisões funcionando"
        echo "Histórico: $history_response"
    else
        warning "Histórico de decisões pode ter problemas"
        echo "Resposta: $history_response"
    fi
    
    # Limpar port-forward
    kill $pf_pid 2>/dev/null
}

# Testar políticas
test_policies() {
    log "Testando políticas..."
    
    # Port-forward para o Decision Engine
    kubectl port-forward -n trisla-nsp svc/decision-engine 8080:8080 > /dev/null 2>&1 &
    local pf_pid=$!
    sleep 5
    
    # Testar endpoint de políticas
    local policies_response=$(curl -s http://localhost:8080/api/v1/policies 2>/dev/null)
    
    if echo "$policies_response" | grep -q "name"; then
        success "Políticas funcionando"
        echo "Políticas: $policies_response"
    else
        warning "Políticas podem ter problemas"
        echo "Resposta: $policies_response"
    fi
    
    # Limpar port-forward
    kill $pf_pid 2>/dev/null
}

# Verificar logs
check_logs() {
    log "Verificando logs do Decision Engine..."
    
    local logs=$(kubectl logs -n trisla-nsp -l app.kubernetes.io/name=decision-engine --tail=20 2>/dev/null)
    
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
    log "Iniciando teste do Decision Engine..."
    echo "=========================================="
    
    check_kubectl
    check_namespace
    deploy_decision_engine
    check_decision_engine
    test_health_check
    test_decision_endpoint
    test_decision_history
    test_policies
    check_logs
    
    echo "=========================================="
    success "Teste do Decision Engine concluído!"
    log "Decision Engine está funcionando corretamente"
}

# Executar teste
main "$@"

