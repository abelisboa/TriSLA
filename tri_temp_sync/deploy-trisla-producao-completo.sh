#!/bin/bash
set -e
LOG_FILE="/home/porvir5g/gtp5g/trisla/deploy-producao.log"
exec > >(tee -a "$LOG_FILE")
exec 2>&1

log() { echo "[$(date +'%H:%M:%S')] $1"; }
log_error() { echo "[$(date +'%H:%M:%S')] ERROR: $1" >&2; }
log_success() { echo "[$(date +'%H:%M:%S')] ✅ $1"; }

log "======================================================================"
log "DEPLOY TRI-SLA COMPLETO - PRODUÇÃO REAL NO NASP"
log "======================================================================"

export GHCR_TOKEN="${GHCR_TOKEN:-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}"

log ""
log "FASE 0: Pré-Checagem"
log "======================================================================"
kubectl get nodes -o wide || { log_error "Cluster inacessível"; exit 1; }
kubectl get ns | grep -q trisla || kubectl create ns trisla
kubectl delete pod -n trisla --all --force --grace-period=0 2>/dev/null || true
sleep 3
log_success "Pré-checagem concluída"

log ""
log "FASE 1: Instalar Dependências"
log "======================================================================"
sudo apt update -y >/dev/null 2>&1
sudo apt install -y jq curl netcat-openbsd python3-pip >/dev/null 2>&1 || true
command -v helm &>/dev/null || sudo snap install helm --classic >/dev/null 2>&1 || true
log_success "Dependências verificadas"

log ""
log "FASE 2: Baixar Imagens do GHCR (tag: nasp-a1 ou latest)"
log "======================================================================"
# Criar secret GHCR no Kubernetes
kubectl delete secret ghcr-secret -n trisla --ignore-not-found=true
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=abelisboa \
  --docker-password="$GHCR_TOKEN" \
  -n trisla 2>&1
log_success "Secret GHCR criado"

# Usar ctr para puxar imagens (containerd)
IMAGES=("sem-csmf" "ml-nsmf" "decision-engine" "bc-nssmf" "sla-agent-layer" "nasp-adapter" "ui-dashboard")
for i in "${IMAGES[@]}"; do
    IMAGE="ghcr.io/abelisboa/trisla-$i:nasp-a1"
    log "Baixando $IMAGE com ctr..."
    if sudo ctr -n k8s.io images pull "$IMAGE" --user "abelisboa:$GHCR_TOKEN" 2>&1; then
        log_success "Imagem $i baixada (nasp-a1)"
    else
        log "Tentando :latest para $i..."
        LATEST="ghcr.io/abelisboa/trisla-$i:latest"
        if sudo ctr -n k8s.io images pull "$LATEST" --user "abelisboa:$GHCR_TOKEN" 2>&1; then
            log_success "Imagem $i baixada (latest)"
        else
            log_error "Falha ao baixar $i"
        fi
    fi
done
sudo ctr -n k8s.io images ls | grep trisla
log_success "Imagens verificadas"

log ""
log "FASE 3: Preparar Helm Chart"
log "======================================================================"
cd /home/porvir5g/gtp5g/trisla/helm/trisla || exit 1
cp values-nasp.yaml values-nasp.yaml.backup 2>/dev/null || true

# Ajustar para usar nasp-a1 se disponível, senão latest
if sudo ctr -n k8s.io images ls | grep -q "nasp-a1"; then
    sed -i 's/:latest/:nasp-a1/g' values-nasp.yaml
    sed -i 's/:local/:nasp-a1/g' values-nasp.yaml
    log "Usando tag nasp-a1"
else
    log "Usando tag latest (nasp-a1 não disponível)"
fi

log_success "Helm Chart preparado"

log ""
log "FASE 4: Deploy Helm"
log "======================================================================"
helm upgrade --install trisla ./ \
  -n trisla \
  -f values-nasp.yaml \
  --create-namespace \
  --cleanup-on-fail \
  --wait \
  --timeout 10m \
  2>&1 | tail -50
sleep 10
log_success "Deploy Helm concluído"

log ""
log "FASE 5: Validação dos Pods"
log "======================================================================"
kubectl get pods -n trisla -o wide
kubectl get svc -n trisla

log ""
log "FASE 6: Testes de Endpoint"
log "======================================================================"
sleep 15  # Aguardar pods iniciarem
for ep in "trisla-sem-csmf:8080" "trisla-ml-nsmf:8081" "trisla-decision-engine:8082" "trisla-bc-nssmf:8545"; do
    svc=$(echo $ep | cut -d: -f1)
    port=$(echo $ep | cut -d: -f2)
    log "Testando $svc:$port..."
    if timeout 3 kubectl run curl-test-$svc --rm -i --restart=Never --image=curlimages/curl:latest --namespace=trisla -- curl -s "http://$svc.trisla.svc.cluster.local:$port/health" 2>/dev/null | head -1; then
        log_success "$svc OK"
    else
        log "⚠️  $svc não respondeu ainda"
    fi
    kubectl delete pod curl-test-$svc -n trisla 2>/dev/null || true
done

log ""
log "FASE 7: Validação Final"
log "======================================================================"
TOTAL=$(kubectl get pods -n trisla --no-headers 2>/dev/null | wc -l)
READY=$(kubectl get pods -n trisla --no-headers 2>/dev/null | awk '{print $2}' | grep -cE "1/1|2/2|3/3" || echo "0")
RUNNING=$(kubectl get pods -n trisla --no-headers 2>/dev/null | grep -c "Running" || echo "0")
ERROR=$(kubectl get pods -n trisla --no-headers 2>/dev/null | grep -E "CrashLoopBackOff|ImagePullBackOff|Error" | wc -l)
log "Total: $TOTAL | Running: $RUNNING | Ready: $READY | Erros: $ERROR"

if [[ $ERROR -gt 0 ]]; then
    log ""
    log "⚠️  Diagnosticando pods com erro..."
    kubectl get pods -n trisla --no-headers | grep -E "CrashLoopBackOff|ImagePullBackOff|Error" | head -3 | while read pod status rest; do
        log "--- $pod ---"
        kubectl logs "$pod" -n trisla --tail=20 2>&1 | head -15
    done
fi

log ""
log "======================================================================"
log "STATUS FINAL"
log "======================================================================"
kubectl get pods -n trisla -o wide
kubectl get svc -n trisla
kubectl get events -n trisla --sort-by=.lastTimestamp | tail -10

