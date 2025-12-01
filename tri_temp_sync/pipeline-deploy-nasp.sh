#!/bin/bash

set -e

LOG_FILE="/home/porvir5g/gtp5g/trisla/pipeline-deploy.log"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "Pipeline de Deploy TriSLA no NASP - Início"
log "=========================================="

cd /home/porvir5g/gtp5g/trisla || { log_error "Diretório não encontrado"; exit 1; }

log "Verificando values-nasp.yaml..."
if grep -q "ghcr.io/abelisboa" helm/trisla/values-nasp.yaml; then
    log "✓ values-nasp.yaml alinhado com GHCR"
else
    log_error "values-nasp.yaml não alinhado"
    exit 1
fi

if [[ -z "$GHCR_TOKEN" ]]; then
    log_error "GHCR_TOKEN não definido"
    exit 1
fi

log "Limpando namespace..."
kubectl delete namespace trisla --ignore-not-found=true || true
sleep 3

log "Criando namespace..."
kubectl create namespace trisla || log "Namespace existe"

log "Criando secret GHCR..."
kubectl delete secret ghcr-secret -n trisla --ignore-not-found=true || true
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=abelisboa \
  --docker-password="$GHCR_TOKEN" \
  -n trisla

log "✓ Secret criado"

log "Executando deploy Helm..."
helm upgrade --install trisla ./helm/trisla \
  -n trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --create-namespace \
  --wait \
  --timeout 20m 2>&1 | tee -a "$LOG_FILE"

sleep 10

log "Validação dos Pods:"
kubectl get pods -n trisla -o wide 2>&1 | tee -a "$LOG_FILE"

log "Validação dos Serviços:"
kubectl get svc -n trisla 2>&1 | tee -a "$LOG_FILE"

TOTAL_PODS=$(kubectl get pods -n trisla --no-headers 2>/dev/null | wc -l)
READY_PODS=$(kubectl get pods -n trisla --no-headers 2>/dev/null | awk '{print $2}' | grep -c "1/1\|2/2" || echo "0")
ERROR_PODS=$(kubectl get pods -n trisla --no-headers 2>/dev/null | grep -E "CrashLoopBackOff|ImagePullBackOff|Error" | wc -l)

log "Total: $TOTAL_PODS | Ready: $READY_PODS | Erros: $ERROR_PODS"

if [[ $ERROR_PODS -gt 0 ]]; then
    log "Diagnosticando pods com erro..."
    for pod in $(kubectl get pods -n trisla --no-headers 2>/dev/null | grep -E "CrashLoopBackOff|ImagePullBackOff|Error" | awk '{print $1}'); do
        log "--- $pod ---"
        kubectl describe pod "$pod" -n trisla 2>&1 | grep -A 10 "Events:" | tee -a "$LOG_FILE"
        kubectl logs "$pod" -n trisla --tail=50 2>&1 | tee -a "$LOG_FILE"
    done
fi

log "Pipeline concluída"
