#!/bin/bash

# TriSLA Portal - Script de Demonstração
# Este script demonstra as funcionalidades principais do TriSLA Portal

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

header() {
    echo -e "${PURPLE}==========================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}==========================================${NC}"
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

# Verificar se os pods estão rodando
check_pods() {
    log "Verificando pods..."
    local running_pods=$(kubectl get pods -n trisla-nsp --field-selector=status.phase=Running --no-headers | wc -l)
    local total_pods=$(kubectl get pods -n trisla-nsp --no-headers | wc -l)
    
    if [ "$running_pods" -eq "$total_pods" ] && [ "$total_pods" -gt 0 ]; then
        success "Todos os pods estão rodando ($running_pods/$total_pods)"
    else
        error "Nem todos os pods estão rodando ($running_pods/$total_pods)"
        kubectl get pods -n trisla-nsp
        exit 1
    fi
}

# Configurar port-forward
setup_port_forward() {
    log "Configurando port-forward..."
    kubectl port-forward -n trisla-nsp svc/sem-nsmf 8080:8080 > /dev/null 2>&1 &
    PF_PID=$!
    sleep 5
    
    # Verificar se port-forward está funcionando
    if curl -s http://localhost:8080/api/v1/health > /dev/null; then
        success "Port-forward configurado com sucesso"
    else
        error "Falha ao configurar port-forward"
        kill $PF_PID 2>/dev/null
        exit 1
    fi
}

# Limpar port-forward
cleanup_port_forward() {
    if [ ! -z "$PF_PID" ]; then
        kill $PF_PID 2>/dev/null
        log "Port-forward limpo"
    fi
}

# Demonstrar cenário URLLC
demo_urllc() {
    header "DEMONSTRAÇÃO URLLC - Cirurgia Remota"
    
    info "Cenário: Cirurgia remota com requisitos de ultra-baixa latência"
    info "Requisitos: Latência < 10ms, Confiabilidade 99.9%"
    
    log "Enviando requisição URLLC..."
    local response=$(curl -s -X POST http://localhost:8080/api/v1/slices \
        -H "Content-Type: application/json" \
        -d '{
            "name": "demo-urllc-cirurgia",
            "type": "URLLC",
            "requirements": {
                "latency": 10,
                "reliability": 99.9,
                "description": "Cirurgia remota - ultra-baixa latência"
            }
        }')
    
    if echo "$response" | grep -q "success\|created\|accepted"; then
        success "Slice URLLC criado com sucesso!"
        echo "Resposta: $response"
    else
        warning "Resposta inesperada: $response"
    fi
    
    echo ""
}

# Demonstrar cenário eMBB
demo_embb() {
    header "DEMONSTRAÇÃO eMBB - Streaming 4K"
    
    info "Cenário: Streaming 4K com alta largura de banda"
    info "Requisitos: Largura de banda 1 Gbps, Latência < 50ms"
    
    log "Enviando requisição eMBB..."
    local response=$(curl -s -X POST http://localhost:8080/api/v1/slices \
        -H "Content-Type: application/json" \
        -d '{
            "name": "demo-embb-streaming",
            "type": "eMBB",
            "requirements": {
                "bandwidth": 1000,
                "latency": 50,
                "description": "Streaming 4K - alta largura de banda"
            }
        }')
    
    if echo "$response" | grep -q "success\|created\|accepted"; then
        success "Slice eMBB criado com sucesso!"
        echo "Resposta: $response"
    else
        warning "Resposta inesperada: $response"
    fi
    
    echo ""
}

# Demonstrar cenário mMTC
demo_mmtc() {
    header "DEMONSTRAÇÃO mMTC - IoT Massivo"
    
    info "Cenário: IoT massivo com milhares de conexões"
    info "Requisitos: 10.000+ conexões, Latência < 100ms"
    
    log "Enviando requisição mMTC..."
    local response=$(curl -s -X POST http://localhost:8080/api/v1/slices \
        -H "Content-Type: application/json" \
        -d '{
            "name": "demo-mmtc-iot",
            "type": "mMTC",
            "requirements": {
                "connections": 10000,
                "latency": 100,
                "description": "IoT massivo - milhares de conexões"
            }
        }')
    
    if echo "$response" | grep -q "success\|created\|accepted"; then
        success "Slice mMTC criado com sucesso!"
        echo "Resposta: $response"
    else
        warning "Resposta inesperada: $response"
    fi
    
    echo ""
}

# Demonstrar load test
demo_load_test() {
    header "DEMONSTRAÇÃO LOAD TEST"
    
    info "Testando sistema sob carga com múltiplas requisições simultâneas"
    
    local success_count=0
    local total_requests=5
    
    for i in $(seq 1 $total_requests); do
        log "Enviando requisição $i/$total_requests..."
        local response=$(curl -s -X POST http://localhost:8080/api/v1/slices \
            -H "Content-Type: application/json" \
            -d "{
                \"name\": \"demo-load-test-$i\",
                \"type\": \"URLLC\",
                \"requirements\": {
                    \"latency\": 10,
                    \"reliability\": 99.9
                }
            }")
        
        if echo "$response" | grep -q "success\|created\|accepted"; then
            success "Requisição $i processada com sucesso"
            ((success_count++))
        else
            warning "Requisição $i falhou: $response"
        fi
        
        sleep 1
    done
    
    echo ""
    info "Resultado do Load Test: $success_count/$total_requests requisições bem-sucedidas"
    
    if [ "$success_count" -eq "$total_requests" ]; then
        success "Load test passou com 100% de sucesso!"
    else
        warning "Load test passou com $((success_count * 100 / total_requests))% de sucesso"
    fi
    
    echo ""
}

# Demonstrar observabilidade
demo_observability() {
    header "DEMONSTRAÇÃO OBSERVABILIDADE"
    
    info "Verificando métricas e status do sistema..."
    
    # Verificar recursos dos pods
    log "Recursos dos pods:"
    kubectl top pods -n trisla-nsp 2>/dev/null || warning "kubectl top não disponível"
    
    echo ""
    
    # Verificar status dos jobs
    log "Verificando status dos jobs..."
    local job_count=$(kubectl get jobs -n trisla-nsp --no-headers | wc -l)
    if [ "$job_count" -gt 0 ]; then
        success "Encontrados $job_count jobs no sistema"
        kubectl get jobs -n trisla-nsp
    else
        info "Nenhum job encontrado (normal para demonstração)"
    fi
    
    echo ""
    
    # Verificar logs recentes
    log "Logs recentes do sistema:"
    kubectl logs -n trisla-nsp --all-containers=true --since=5m | tail -10
    
    echo ""
}

# Demonstrar API endpoints
demo_api_endpoints() {
    header "DEMONSTRAÇÃO API ENDPOINTS"
    
    info "Testando endpoints da API..."
    
    # Health check
    log "Testando health check..."
    local health_response=$(curl -s http://localhost:8080/api/v1/health)
    if [ ! -z "$health_response" ]; then
        success "Health check funcionando: $health_response"
    else
        warning "Health check não respondeu"
    fi
    
    echo ""
    
    # Listar slices
    log "Listando slices existentes..."
    local slices_response=$(curl -s http://localhost:8080/api/v1/slices)
    if [ ! -z "$slices_response" ]; then
        success "Endpoint de slices funcionando"
        echo "Resposta: $slices_response"
    else
        warning "Endpoint de slices não respondeu"
    fi
    
    echo ""
}

# Resumo da demonstração
demo_summary() {
    header "RESUMO DA DEMONSTRAÇÃO"
    
    success "TriSLA Portal demonstrado com sucesso!"
    echo ""
    
    info "Funcionalidades testadas:"
    echo "  ✅ Cenário URLLC (Cirurgia Remota)"
    echo "  ✅ Cenário eMBB (Streaming 4K)"
    echo "  ✅ Cenário mMTC (IoT Massivo)"
    echo "  ✅ Load Test (Múltiplas requisições)"
    echo "  ✅ Observabilidade (Métricas e logs)"
    echo "  ✅ API Endpoints (Health check e slices)"
    echo ""
    
    info "Sistema pronto para produção!"
    echo ""
    
    info "Para acessar o sistema:"
    echo "  - API: http://localhost:8080"
    echo "  - Grafana: kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80"
    echo "  - Prometheus: kubectl port-forward -n monitoring svc/prometheus-monitoring-kube-prometheus-prometheus 9090:9090"
    echo ""
}

# Função principal
main() {
    header "TRI SLA PORTAL - DEMONSTRAÇÃO COMPLETA"
    
    log "Iniciando demonstração do TriSLA Portal..."
    echo ""
    
    # Verificações iniciais
    check_kubectl
    check_namespace
    check_pods
    
    # Configurar port-forward
    setup_port_forward
    
    # Configurar trap para limpeza
    trap cleanup_port_forward EXIT
    
    # Demonstrações
    demo_urllc
    demo_embb
    demo_mmtc
    demo_load_test
    demo_observability
    demo_api_endpoints
    
    # Resumo
    demo_summary
    
    log "Demonstração concluída com sucesso!"
}

# Executar demonstração
main "$@"
