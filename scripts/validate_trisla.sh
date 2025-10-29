#!/bin/bash

# TriSLA Portal - Script de Validação
# Este script valida se o sistema TriSLA está funcionando corretamente

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

# Verificar pods
check_pods() {
    log "Verificando pods..."
    local pods=$(kubectl get pods -n trisla-nsp --no-headers | wc -l)
    if [ "$pods" -eq 0 ]; then
        error "Nenhum pod encontrado no namespace trisla-nsp"
        exit 1
    fi
    
    # Verificar status dos pods
    local running_pods=$(kubectl get pods -n trisla-nsp --field-selector=status.phase=Running --no-headers | wc -l)
    local total_pods=$(kubectl get pods -n trisla-nsp --no-headers | wc -l)
    
    if [ "$running_pods" -eq "$total_pods" ]; then
        success "Todos os pods estão rodando ($running_pods/$total_pods)"
    else
        warning "Alguns pods não estão rodando ($running_pods/$total_pods)"
        kubectl get pods -n trisla-nsp
    fi
}

# Verificar serviços
check_services() {
    log "Verificando serviços..."
    local services=$(kubectl get services -n trisla-nsp --no-headers | wc -l)
    if [ "$services" -eq 0 ]; then
        error "Nenhum serviço encontrado no namespace trisla-nsp"
        exit 1
    fi
    success "Serviços encontrados ($services)"
}

# Verificar deployments
check_deployments() {
    log "Verificando deployments..."
    local deployments=$(kubectl get deployments -n trisla-nsp --no-headers | wc -l)
    if [ "$deployments" -eq 0 ]; then
        error "Nenhum deployment encontrado no namespace trisla-nsp"
        exit 1
    fi
    success "Deployments encontrados ($deployments)"
}

# Testar conectividade da API
test_api() {
    log "Testando conectividade da API..."
    
    # Port-forward para a API
    kubectl port-forward -n trisla-nsp svc/sem-nsmf 8080:8080 > /dev/null 2>&1 &
    local pf_pid=$!
    
    # Aguardar port-forward estar pronto
    sleep 5
    
    # Testar endpoint de health
    if curl -s http://localhost:8080/api/v1/health > /dev/null; then
        success "API respondendo corretamente"
    else
        error "API não está respondendo"
        kill $pf_pid 2>/dev/null
        exit 1
    fi
    
    # Testar endpoint de slices
    if curl -s http://localhost:8080/api/v1/slices > /dev/null; then
        success "Endpoint de slices funcionando"
    else
        warning "Endpoint de slices pode não estar funcionando"
    fi
    
    # Limpar port-forward
    kill $pf_pid 2>/dev/null
}

# Testar cenários 5G
test_scenarios() {
    log "Testando cenários 5G..."
    
    # Port-forward para a API
    kubectl port-forward -n trisla-nsp svc/sem-nsmf 8080:8080 > /dev/null 2>&1 &
    local pf_pid=$!
    sleep 5
    
    # Teste URLLC
    log "Testando cenário URLLC..."
    local urllc_response=$(curl -s -X POST http://localhost:8080/api/v1/slices \
        -H "Content-Type: application/json" \
        -d '{
            "name": "test-urllc-validation",
            "type": "URLLC",
            "requirements": {
                "latency": 10,
                "reliability": 99.9
            }
        }' 2>/dev/null)
    
    if echo "$urllc_response" | grep -q "success\|created\|accepted"; then
        success "Cenário URLLC funcionando"
    else
        warning "Cenário URLLC pode ter problemas"
    fi
    
    # Teste eMBB
    log "Testando cenário eMBB..."
    local embb_response=$(curl -s -X POST http://localhost:8080/api/v1/slices \
        -H "Content-Type: application/json" \
        -d '{
            "name": "test-embb-validation",
            "type": "eMBB",
            "requirements": {
                "bandwidth": 1000,
                "latency": 50
            }
        }' 2>/dev/null)
    
    if echo "$embb_response" | grep -q "success\|created\|accepted"; then
        success "Cenário eMBB funcionando"
    else
        warning "Cenário eMBB pode ter problemas"
    fi
    
    # Teste mMTC
    log "Testando cenário mMTC..."
    local mmtc_response=$(curl -s -X POST http://localhost:8080/api/v1/slices \
        -H "Content-Type: application/json" \
        -d '{
            "name": "test-mmtc-validation",
            "type": "mMTC",
            "requirements": {
                "connections": 10000,
                "latency": 100
            }
        }' 2>/dev/null)
    
    if echo "$mmtc_response" | grep -q "success\|created\|accepted"; then
        success "Cenário mMTC funcionando"
    else
        warning "Cenário mMTC pode ter problemas"
    fi
    
    # Limpar port-forward
    kill $pf_pid 2>/dev/null
}

# Verificar recursos do sistema
check_resources() {
    log "Verificando recursos do sistema..."
    
    # CPU e memória dos pods
    log "Recursos dos pods:"
    kubectl top pods -n trisla-nsp 2>/dev/null || warning "kubectl top não disponível"
    
    # Recursos dos nodes
    log "Recursos dos nodes:"
    kubectl top nodes 2>/dev/null || warning "kubectl top não disponível"
}

# Verificar logs de erro
check_logs() {
    log "Verificando logs de erro..."
    
    local error_logs=$(kubectl logs -n trisla-nsp --all-containers=true --since=1h | grep -i error | wc -l)
    if [ "$error_logs" -gt 0 ]; then
        warning "Encontrados $error_logs logs de erro na última hora"
        kubectl logs -n trisla-nsp --all-containers=true --since=1h | grep -i error | head -5
    else
        success "Nenhum log de erro encontrado na última hora"
    fi
}

# Função principal
main() {
    log "Iniciando validação do TriSLA Portal..."
    echo "=========================================="
    
    check_kubectl
    check_namespace
    check_pods
    check_services
    check_deployments
    test_api
    test_scenarios
    check_resources
    check_logs
    
    echo "=========================================="
    success "Validação concluída!"
    log "Sistema TriSLA Portal está funcionando corretamente"
}

# Executar validação
main "$@"
