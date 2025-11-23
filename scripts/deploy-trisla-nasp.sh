#!/bin/bash
#
# TriSLA — Deploy Script NASP v3.0
# Script completo para deploy do TriSLA no ambiente NASP (Node1/Node2)
#
# Uso:
#   ./scripts/deploy-trisla-nasp.sh [--pre-flight] [--helm-install] [--helm-upgrade] [--health-check] [--logs]
#

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configurações
NAMESPACE="${TRISLA_NAMESPACE:-trisla}"
HELM_RELEASE="${TRISLA_HELM_RELEASE:-trisla-prod}"
HELM_CHART_VERSION="${TRISLA_CHART_VERSION:-v1.0.0}"
GHCR_REGISTRY="${GHCR_REGISTRY:-ghcr.io/abelisboa}"
# Para deploy NASP, usar values-nasp.yaml; para produção genérica, usar values-production.yaml
VALUES_FILE="${TRISLA_VALUES_FILE:-helm/trisla/values-nasp.yaml}"

# Flags
DO_PRE_FLIGHT=false
DO_HELM_INSTALL=false
DO_HELM_UPGRADE=false
DO_HEALTH_CHECK=false
SHOW_LOGS=false

# Funções utilitárias
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Pre-flight checks
pre_flight_check() {
    log_info "🔍 Executando pre-flight checks..."
    
    # Verificar kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl não encontrado. Instale kubectl primeiro."
        exit 1
    fi
    KUBECTL_VERSION=$(kubectl version --client -o json | jq -r '.clientVersion.gitVersion' 2>/dev/null || echo "unknown")
    log_info "kubectl: $KUBECTL_VERSION"
    
    # Verificar acesso ao cluster
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Não é possível acessar o cluster Kubernetes"
        log_error "Verifique: kubectl config get-contexts"
        exit 1
    fi
    log_info "✅ Cluster acessível"
    
    # Verificar Helm
    if ! command -v helm &> /dev/null; then
        log_error "Helm não encontrado. Instale Helm primeiro."
        exit 1
    fi
    HELM_VERSION=$(helm version --short 2>/dev/null || echo "unknown")
    log_info "Helm: $HELM_VERSION"
    
    # Verificar namespace
    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_info "✅ Namespace '$NAMESPACE' existe"
    else
        log_warn "Namespace '$NAMESPACE' não existe (será criado durante o deploy)"
    fi
    
    # Verificar nós
    NODES=$(kubectl get nodes --no-headers 2>/dev/null | wc -l || echo "0")
    if [ "$NODES" -lt 1 ]; then
        log_error "Nenhum nó encontrado no cluster"
        exit 1
    fi
    log_info "✅ Nós disponíveis: $NODES"
    
    # Verificar values file
    if [ ! -f "$VALUES_FILE" ]; then
        log_warn "Arquivo values não encontrado: $VALUES_FILE"
        log_warn "Será usado values padrão do chart"
    else
        log_info "✅ Values file encontrado: $VALUES_FILE"
    fi
    
    log_info "✅ Pre-flight checks concluídos com sucesso"
}

# Sincronizar imagens do GHCR (se necessário)
sync_ghcr_images() {
    log_info "🔄 Sincronização de imagens do GHCR..."
    
    # Verificar se é necessário login no GHCR
    if [ -n "${GITHUB_TOKEN:-}" ]; then
        log_info "🔐 Fazendo login no GHCR..."
        echo "$GITHUB_TOKEN" | docker login ghcr.io -u "${GITHUB_USER:-USERNAME}" --password-stdin || {
            log_warn "Falha ao fazer login no GHCR (continuando mesmo assim)"
        }
    else
        log_warn "GITHUB_TOKEN não definido (pode ser necessário para pull de imagens)"
    fi
    
    log_info "ℹ️ Se as imagens não estiverem acessíveis, execute: scripts/sync-ghcr-images.sh"
}

# Helm install
helm_install() {
    log_info "📦 Instalando TriSLA via Helm..."
    
    # Adicionar Helm repo
    log_info "Adicionando Helm repository..."
    helm repo add trisla-oci "oci://${GHCR_REGISTRY}/helm-charts" 2>/dev/null || {
        log_warn "Repo já existe (ignorando)"
    }
    helm repo update
    
    # Criar namespace se não existir
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_info "Criando namespace '$NAMESPACE'..."
        kubectl create namespace "$NAMESPACE"
    fi
    
    # Criar secret para GHCR (se token fornecido)
    if [ -n "${GITHUB_TOKEN:-}" ]; then
        log_info "Criando secret para GHCR..."
        kubectl create secret docker-registry ghcr-secret \
            --docker-server=ghcr.io \
            --docker-username="${GITHUB_USER:-USERNAME}" \
            --docker-password="$GITHUB_TOKEN" \
            --namespace="$NAMESPACE" \
            2>/dev/null || {
            log_warn "Secret já existe (ignorando)"
        }
    fi
    
    # Instalar via Helm
    log_info "Executando helm install..."
    if [ -f "$VALUES_FILE" ]; then
        helm install "$HELM_RELEASE" \
            "oci://${GHCR_REGISTRY}/helm-charts/trisla" \
            --version "$HELM_CHART_VERSION" \
            --namespace "$NAMESPACE" \
            --values "$VALUES_FILE" \
            --wait \
            --timeout 10m
    else
        helm install "$HELM_RELEASE" \
            "oci://${GHCR_REGISTRY}/helm-charts/trisla" \
            --version "$HELM_CHART_VERSION" \
            --namespace "$NAMESPACE" \
            --wait \
            --timeout 10m
    fi
    
    log_info "✅ Helm install concluído"
}

# Helm upgrade
helm_upgrade() {
    log_info "🔄 Atualizando TriSLA via Helm..."
    
    # Verificar se release existe
    if ! helm list -n "$NAMESPACE" | grep -q "$HELM_RELEASE"; then
        log_error "Release '$HELM_RELEASE' não encontrada no namespace '$NAMESPACE'"
        log_error "Execute com --helm-install primeiro"
        exit 1
    fi
    
    # Atualizar Helm repos
    helm repo update
    
    # Upgrade
    log_info "Executando helm upgrade..."
    if [ -f "$VALUES_FILE" ]; then
        helm upgrade "$HELM_RELEASE" \
            "oci://${GHCR_REGISTRY}/helm-charts/trisla" \
            --version "$HELM_CHART_VERSION" \
            --namespace "$NAMESPACE" \
            --values "$VALUES_FILE" \
            --wait \
            --timeout 10m
    else
        helm upgrade "$HELM_RELEASE" \
            "oci://${GHCR_REGISTRY}/helm-charts/trisla" \
            --version "$HELM_CHART_VERSION" \
            --namespace "$NAMESPACE" \
            --wait \
            --timeout 10m
    fi
    
    log_info "✅ Helm upgrade concluído"
}

# Health checks
health_check() {
    log_info "🏥 Executando health checks..."
    
    SERVICES=(
        "sem-csmf:8080"
        "ml-nsmf:8081"
        "decision-engine:8082"
        "bc-nsmf:8083"
        "nasp-adapter:8084"
    )
    
    ALL_HEALTHY=true
    
    for service in "${SERVICES[@]}"; do
        name="${service%%:*}"
        port="${service##*:}"
        
        log_info "Verificando $name..."
        if kubectl run health-check-$name \
            --image=curlimages/curl:latest \
            --rm -i --restart=Never \
            -n "$NAMESPACE" \
            -- curl -sf --max-time 5 http://$name:$port/health > /dev/null 2>&1; then
            log_info "  ✅ $name: HEALTHY"
        else
            log_error "  ❌ $name: UNHEALTHY"
            ALL_HEALTHY=false
        fi
    done
    
    # Status dos pods
    log_info "Status dos pods:"
    kubectl get pods -n "$NAMESPACE" -o wide
    
    if [ "$ALL_HEALTHY" = false ]; then
        log_error "Alguns serviços não estão saudáveis"
        return 1
    fi
    
    log_info "✅ Todos os health checks passaram"
    return 0
}

# Mostrar logs
show_logs() {
    log_info "📋 Logs dos pods..."
    
    PODS=$(kubectl get pods -n "$NAMESPACE" -o name | head -5)
    
    for pod in $PODS; do
        pod_name="${pod#pod/}"
        log_info "Logs de $pod_name:"
        kubectl logs "$pod_name" -n "$NAMESPACE" --tail=20
        echo ""
    done
}

# Status geral
show_status() {
    log_info "📊 Status do deploy:"
    
    echo ""
    log_info "Helm Release:"
    helm status "$HELM_RELEASE" -n "$NAMESPACE" 2>/dev/null || log_warn "Release não encontrada"
    
    echo ""
    log_info "Pods:"
    kubectl get pods -n "$NAMESPACE" -o wide
    
    echo ""
    log_info "Services:"
    kubectl get svc -n "$NAMESPACE"
    
    echo ""
    log_info "Para mais detalhes:"
    echo "  kubectl get all -n $NAMESPACE"
    echo "  helm status $HELM_RELEASE -n $NAMESPACE"
}

# Help
show_help() {
    cat <<EOF
TriSLA — Deploy Script NASP v3.0

Uso:
  $0 [OPÇÕES]

Opções:
  --pre-flight        Executa pre-flight checks
  --helm-install      Instala TriSLA via Helm
  --helm-upgrade      Atualiza TriSLA via Helm
  --health-check      Executa health checks após deploy
  --logs              Mostra logs dos pods
  --all               Executa todas as operações (pre-flight + install + health-check)
  --help              Mostra esta ajuda

Variáveis de Ambiente:
  TRISLA_NAMESPACE          Namespace Kubernetes (padrão: trisla)
  TRISLA_HELM_RELEASE       Nome do Helm release (padrão: trisla-prod)
  TRISLA_CHART_VERSION      Versão do Helm chart (padrão: v1.0.0)
  GHCR_REGISTRY            Registry GHCR (padrão: ghcr.io/abelisboa)
  TRISLA_VALUES_FILE       Arquivo values.yaml (padrão para NASP: helm/trisla/values-nasp.yaml)
  GITHUB_TOKEN             Token do GitHub para GHCR (opcional)
  GITHUB_USER              Usuário do GitHub para GHCR (opcional)

Exemplos:
  # Deploy completo
  $0 --all

  # Apenas pre-flight
  $0 --pre-flight

  # Instalar
  $0 --pre-flight --helm-install --health-check

  # Atualizar
  $0 --helm-upgrade --health-check

EOF
}

# Main
main() {
    log_info "🚀 TriSLA Deploy Script NASP v3.0"
    log_info "Namespace: $NAMESPACE"
    log_info "Helm Release: $HELM_RELEASE"
    log_info "Chart Version: $HELM_CHART_VERSION"
    echo ""
    
    # Processar argumentos
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --pre-flight)
                DO_PRE_FLIGHT=true
                shift
                ;;
            --helm-install)
                DO_HELM_INSTALL=true
                shift
                ;;
            --helm-upgrade)
                DO_HELM_UPGRADE=true
                shift
                ;;
            --health-check)
                DO_HEALTH_CHECK=true
                shift
                ;;
            --logs)
                SHOW_LOGS=true
                shift
                ;;
            --all)
                DO_PRE_FLIGHT=true
                DO_HELM_INSTALL=true
                DO_HEALTH_CHECK=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Opção desconhecida: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Executar operações
    if [ "$DO_PRE_FLIGHT" = true ]; then
        pre_flight_check
        sync_ghcr_images
    fi
    
    if [ "$DO_HELM_INSTALL" = true ]; then
        if [ "$DO_HELM_UPGRADE" = true ]; then
            log_error "Não é possível usar --helm-install e --helm-upgrade ao mesmo tempo"
            exit 1
        fi
        helm_install
    fi
    
    if [ "$DO_HELM_UPGRADE" = true ]; then
        helm_upgrade
    fi
    
    if [ "$DO_HEALTH_CHECK" = true ]; then
        sleep 10  # Aguardar pods iniciarem
        health_check
    fi
    
    if [ "$SHOW_LOGS" = true ]; then
        show_logs
    fi
    
    # Status final
    show_status
    
    log_info "✅ Script concluído"
}

# Executar main
main "$@"
