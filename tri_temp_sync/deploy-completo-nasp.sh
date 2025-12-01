#!/bin/bash

set -e

LOG_FILE="/home/porvir5g/gtp5g/trisla/deploy-completo-nasp.log"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✓ $1" | tee -a "$LOG_FILE"
}

log_phase() {
    echo ""
    echo "======================================================================"
    echo "FASE $1: $2"
    echo "======================================================================"
}

cd /home/porvir5g/gtp5g/trisla || { log_error "Diretório não encontrado"; exit 1; }

log "=========================================="
log "Deploy Completo TriSLA no NASP - Início"
log "=========================================="

# FASE 0 — Pré-Checagem
log_phase "0" "Pré-Checagem obrigatória"
log "1. Verificando acesso ao cluster..."
kubectl get nodes -o wide 2>&1 | tee -a "$LOG_FILE" || { log_error "Acesso ao cluster falhou"; exit 1; }
log_success "Cluster acessível"

log "2. Validando namespace..."
kubectl get ns | grep -q trisla || kubectl create ns trisla
log_success "Namespace validado"

log "3. Limpando pods antigos..."
kubectl delete pod -n trisla --all --force --grace-period=0 2>&1 | tee -a "$LOG_FILE" || true
sleep 3
log_success "Pods antigos removidos"

# FASE 1 — Dependências
log_phase "1" "Instalar dependências"
log "1. Instalando pacotes essenciais..."
sudo apt update -y 2>&1 | tee -a "$LOG_FILE" || true
sudo apt install -y jq curl netcat-openbsd python3-pip 2>&1 | tee -a "$LOG_FILE" || true
log_success "Pacotes instalados"

log "2. Verificando helm..."
helm version &>/dev/null || sudo snap install helm --classic 2>&1 | tee -a "$LOG_FILE" || true
log_success "Helm verificado"

log "3. Verificando Docker..."
systemctl status docker &>/dev/null || sudo systemctl restart docker 2>&1 | tee -a "$LOG_FILE" || true
sleep 2
log_success "Docker verificado"

log "4. Instalando solcx..."
pip3 install py-solc-x --break-system-packages 2>&1 | tee -a "$LOG_FILE" || \
pip3 install py-solc-x 2>&1 | tee -a "$LOG_FILE" || true
log_success "solcx instalado"

# FASE 2 — Baixar imagens
log_phase "2" "Baixar imagens do GHCR (tag nasp-a1)"
IMAGES=("sem-csmf" "ml-nsmf" "decision-engine" "bc-nssmf" "sla-agent-layer" "nasp-adapter" "ui-dashboard")

for i in "${IMAGES[@]}"; do
    log "Baixando trisla-$i:nasp-a1..."
    docker pull ghcr.io/abelisboa/trisla-$i:nasp-a1 2>&1 | tee -a "$LOG_FILE" || {
        log "Tentando com tag latest..."
        docker pull ghcr.io/abelisboa/trisla-$i:latest 2>&1 | tee -a "$LOG_FILE" || true
    }
done

log "Imagens disponíveis:"
docker images | grep trisla | tee -a "$LOG_FILE"
log_success "Imagens baixadas"

# FASE 3 — Preparar Helm Chart
log_phase "3" "Preparar Helm Chart"
cd /home/porvir5g/gtp5g/trisla/helm/trisla || { log_error "Diretório helm não encontrado"; exit 1; }

log "Instalando yq se necessário..."
if ! command -v yq &>/dev/null; then
    sudo wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
    sudo chmod +x /usr/local/bin/yq
fi

cp values-nasp.yaml values-nasp.yaml.backup

log "Atualizando tags para nasp-a1..."
yq eval '.bcNssmf.image.tag = "nasp-a1"' -i values-nasp.yaml 2>/dev/null || true
yq eval '.decisionEngine.image.tag = "nasp-a1"' -i values-nasp.yaml 2>/dev/null || true
yq eval '.mlNsmf.image.tag = "nasp-a1"' -i values-nasp.yaml 2>/dev/null || true
yq eval '.semCsmf.image.tag = "nasp-a1"' -i values-nasp.yaml 2>/dev/null || true
yq eval '.slaAgentLayer.image.tag = "nasp-a1"' -i values-nasp.yaml 2>/dev/null || true
yq eval '.naspAdapter.image.tag = "nasp-a1"' -i values-nasp.yaml 2>/dev/null || true
yq eval '.uiDashboard.image.tag = "nasp-a1"' -i values-nasp.yaml 2>/dev/null || true

log "Configurando variáveis de produção..."
yq eval '.global.otlpEnabled = true' -i values-nasp.yaml 2>/dev/null || true
yq eval '.global.kafkaEnabled = true' -i values-nasp.yaml 2>/dev/null || true
yq eval '.global.bcEnabled = true' -i values-nasp.yaml 2>/dev/null || true
yq eval '.global.naspMode = "production"' -i values-nasp.yaml 2>/dev/null || true

log_success "values-nasp.yaml configurado"

# FASE 4 — Deploy Helm
log_phase "4" "Deploy completo com Helm"
log "Executando helm upgrade --install..."
helm upgrade --install trisla ./ \
  -n trisla \
  -f values-nasp.yaml \
  --create-namespace \
  --cleanup-on-fail \
  --wait \
  --timeout 10m \
  --debug 2>&1 | tee -a "$LOG_FILE" || log_error "Helm deploy falhou"

sleep 10

# FASE 5 — Validação
log_phase "5" "Validação automática dos pods"
log "Status dos pods:"
kubectl get pods -n trisla -o wide 2>&1 | tee -a "$LOG_FILE"

log "Status dos serviços:"
kubectl get svc -n trisla 2>&1 | tee -a "$LOG_FILE"

log "Eventos recentes:"
kubectl get events -n trisla --sort-by=.lastTimestamp 2>&1 | tail -30 | tee -a "$LOG_FILE"

# FASE 6 — Testes
log_phase "6" "Testes automáticos de endpoints"
sleep 30

for endpoint in "trisla-sem-csmf.trisla.svc.cluster.local:8080/health" \
                "trisla-ml-nsmf.trisla.svc.cluster.local:8081/health" \
                "trisla-decision-engine.trisla.svc.cluster.local:8082/health" \
                "trisla-bc-nssmf.trisla.svc.cluster.local:8083/health"; do
    log "Testando http://$endpoint..."
    curl -s -m 5 http://$endpoint 2>&1 | head -3 || log_error "Falha: $endpoint"
done

# FASE 7 — Validação final
log_phase "7" "Validação final de produção"
MAX_WAIT=300
ELAPSED=0

while [[ $ELAPSED -lt $MAX_WAIT ]]; do
    NOT_READY=$(kubectl get pods -n trisla --no-headers 2>/dev/null | grep -v "1/1\|2/2\|3/3" | grep -v "Completed" | wc -l || echo "999")
    CRASH=$(kubectl get pods -n trisla --no-headers 2>/dev/null | grep -c "CrashLoopBackOff" || echo "0")
    
    if [[ $NOT_READY -eq 0 ]] && [[ $CRASH -eq 0 ]]; then
        log_success "Todos os pods prontos!"
        break
    fi
    
    log "Aguardando... (${ELAPSED}s) - Not Ready: $NOT_READY, Crash: $CRASH"
    kubectl get pods -n trisla
    sleep 15
    ELAPSED=$((ELAPSED + 15))
done

log "=========================================="
log "Status Final"
log "=========================================="
kubectl get pods -n trisla -o wide
kubectl get svc -n trisla

TOTAL=$(kubectl get pods -n trisla --no-headers 2>/dev/null | wc -l)
READY=$(kubectl get pods -n trisla --no-headers 2>/dev/null | awk '{print $2}' | grep -c "1/1\|2/2\|3/3" || echo "0")
CRASH=$(kubectl get pods -n trisla --no-headers 2>/dev/null | grep -c "CrashLoopBackOff" || echo "0")

log "Total: $TOTAL | Ready: $READY | CrashLoop: $CRASH"

if [[ $READY -eq $TOTAL ]] && [[ $CRASH -eq 0 ]] && [[ $TOTAL -gt 0 ]]; then
    log "✅ DEPLOY COMPLETO!"
    exit 0
else
    log "⚠️ DEPLOY PARCIAL"
    exit 1
fi
