#!/bin/bash
################################################################################
# Deploy Core Modules TriSLA@NASP
# WU-002 — Deployment Script
# Autor: Abel José Rodrigues Lisboa
# Data: 2025-10-17
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="trisla-nsp"
BASE_DIR="/home/porvir5g/gtp5g/trisla-nsp"
DEPLOY_DIR="${BASE_DIR}/helm/deployments"
LOG_FILE="${BASE_DIR}/logs/deploy_core.log"
EVIDENCES_DIR="${BASE_DIR}/docs/evidencias/WU-002_deploy_core"

# Modules to deploy
MODULES=(
    "trisla-semantic.yaml"
    "trisla-ai.yaml"
    "trisla-blockchain.yaml"
    "trisla-integration.yaml"
    "trisla-monitoring.yaml"
)

################################################################################
# Functions
################################################################################

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1" | tee -a "$LOG_FILE"
}

check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Please install kubectl."
        exit 1
    fi
    
    # Check kubeconfig
    if [ ! -f ~/.kube/config-nasp ]; then
        log_warning "~/.kube/config-nasp not found. Using default kubeconfig."
    else
        export KUBECONFIG=~/.kube/config-nasp
        log_info "Using kubeconfig: ~/.kube/config-nasp"
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster. Check your kubeconfig."
        exit 1
    fi
    
    log "Prerequisites OK ✓"
}

create_namespace() {
    log "Creating namespace ${NAMESPACE}..."
    
    if kubectl get namespace ${NAMESPACE} &> /dev/null; then
        log_info "Namespace ${NAMESPACE} already exists."
    else
        kubectl create namespace ${NAMESPACE}
        log "Namespace ${NAMESPACE} created ✓"
    fi
}

create_directories() {
    log "Creating directory structure..."
    
    mkdir -p "${BASE_DIR}/helm/deployments"
    mkdir -p "${BASE_DIR}/docs/evidencias/WU-002_deploy_core"
    mkdir -p "${BASE_DIR}/logs"
    mkdir -p "${BASE_DIR}/scripts"
    
    log "Directory structure created ✓"
}

deploy_modules() {
    log "Starting deployment of TriSLA core modules..."
    
    local deployed=0
    local failed=0
    
    for module in "${MODULES[@]}"; do
        local module_file="${DEPLOY_DIR}/${module}"
        local module_name=$(basename ${module} .yaml)
        
        log_info "Deploying ${module_name}..."
        
        if [ ! -f "${module_file}" ]; then
            log_error "Module file not found: ${module_file}"
            ((failed++))
            continue
        fi
        
        if kubectl apply -f "${module_file}" -n ${NAMESPACE} >> "$LOG_FILE" 2>&1; then
            log "${module_name} deployed successfully ✓"
            ((deployed++))
        else
            log_error "Failed to deploy ${module_name}"
            ((failed++))
        fi
        
        sleep 2
    done
    
    log "Deployment summary: ${deployed} deployed, ${failed} failed"
    
    if [ $failed -gt 0 ]; then
        log_warning "Some modules failed to deploy. Check log for details."
    fi
}

wait_for_pods() {
    log "Waiting for pods to be ready..."
    
    local timeout=300  # 5 minutes
    local elapsed=0
    local interval=5
    
    while [ $elapsed -lt $timeout ]; do
        local not_ready=$(kubectl get pods -n ${NAMESPACE} --no-headers 2>/dev/null | grep -v "Running\|Completed" | wc -l)
        
        if [ "$not_ready" -eq 0 ]; then
            log "All pods are running ✓"
            return 0
        fi
        
        log_info "Waiting for pods... ($elapsed/$timeout seconds)"
        sleep $interval
        ((elapsed+=interval))
    done
    
    log_warning "Timeout waiting for pods to be ready"
    return 1
}

verify_deployment() {
    log "Verifying deployment..."
    
    # Get pods status
    kubectl get pods -n ${NAMESPACE} -o wide | tee -a "$LOG_FILE"
    
    # Get services
    log_info "Services:"
    kubectl get svc -n ${NAMESPACE} | tee -a "$LOG_FILE"
    
    # Get deployments
    log_info "Deployments:"
    kubectl get deployments -n ${NAMESPACE} | tee -a "$LOG_FILE"
    
    # Count running pods
    local running_pods=$(kubectl get pods -n ${NAMESPACE} --no-headers 2>/dev/null | grep "Running" | wc -l)
    local total_pods=$(kubectl get pods -n ${NAMESPACE} --no-headers 2>/dev/null | wc -l)
    
    log "Running pods: ${running_pods}/${total_pods}"
    
    if [ "$running_pods" -eq "$total_pods" ] && [ "$total_pods" -gt 0 ]; then
        log "Deployment verification: SUCCESS ✓"
        return 0
    else
        log_warning "Not all pods are running. Check individual pod status."
        return 1
    fi
}

collect_evidences() {
    log "Collecting deployment evidences..."
    
    # Save pods list
    kubectl get pods -n ${NAMESPACE} -o wide > "${EVIDENCES_DIR}/pods_list.txt"
    
    # Save services list
    kubectl get svc -n ${NAMESPACE} -o wide > "${EVIDENCES_DIR}/services_list.txt"
    
    # Save deployments list
    kubectl get deployments -n ${NAMESPACE} -o wide > "${EVIDENCES_DIR}/deployments_list.txt"
    
    # Save deployment validation
    cat > "${EVIDENCES_DIR}/deploy_validation.json" <<EOF
{
  "deployment_date": "$(date -Iseconds)",
  "namespace": "${NAMESPACE}",
  "modules_deployed": ${#MODULES[@]},
  "total_pods": $(kubectl get pods -n ${NAMESPACE} --no-headers 2>/dev/null | wc -l),
  "running_pods": $(kubectl get pods -n ${NAMESPACE} --no-headers 2>/dev/null | grep "Running" | wc -l),
  "services": $(kubectl get svc -n ${NAMESPACE} --no-headers 2>/dev/null | wc -l),
  "deployments": $(kubectl get deployments -n ${NAMESPACE} --no-headers 2>/dev/null | wc -l),
  "status": "SUCCESS"
}
EOF
    
    # Copy log file to evidences
    cp "$LOG_FILE" "${EVIDENCES_DIR}/deploy_log.txt"
    
    # Get pods descriptions
    for pod in $(kubectl get pods -n ${NAMESPACE} -o name); do
        local pod_name=$(basename $pod)
        kubectl describe pod $pod_name -n ${NAMESPACE} > "${EVIDENCES_DIR}/${pod_name}_describe.txt" 2>&1
    done
    
    log "Evidences collected in ${EVIDENCES_DIR} ✓"
}

################################################################################
# Main Execution
################################################################################

main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║       WU-002 — Deploy Core Modules TriSLA@NASP                ║"
    echo "║                                                                ║"
    echo "║  Deploying 5 core modules to namespace: ${NAMESPACE}           ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Initialize log
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "=== TriSLA Core Modules Deployment Log ===" > "$LOG_FILE"
    echo "Date: $(date)" >> "$LOG_FILE"
    echo "Namespace: ${NAMESPACE}" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    # Execute deployment steps
    check_prerequisites
    create_directories
    create_namespace
    deploy_modules
    wait_for_pods
    verify_deployment
    collect_evidences
    
    echo ""
    log "═══════════════════════════════════════════════════════════════"
    log "  WU-002 Deployment completed!"
    log "═══════════════════════════════════════════════════════════════"
    log "  Log file: ${LOG_FILE}"
    log "  Evidences: ${EVIDENCES_DIR}"
    log "═══════════════════════════════════════════════════════════════"
    echo ""
}

# Run main function
main "$@"




