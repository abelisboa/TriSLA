#!/bin/bash
set -euo pipefail

# ============================================
# TriSLA v3.4.0 - Deploy Automático NASP
# ============================================
# Script de instalação automática com autocorreção
# Executa no node1 do NASP via SSH

LOG_FILE="/tmp/trisla-deploy.log"
START_TIME=$(date +%s)

# Determinar caminho do repositório (relativo ao script ou absoluto)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HELM_CHART_PATH="${REPO_ROOT}/helm/trisla"
VALUES_FILE="${REPO_ROOT}/helm/trisla/values-nasp.yaml"
RELEASE_NAME="trisla-portal"
NAMESPACE="trisla"

# Permitir override via variável de ambiente
VALUES_FILE="${TRISLA_VALUES_FILE:-${VALUES_FILE}}"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função de log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

# Função para executar comando e capturar erro
run_cmd() {
    local cmd="$1"
    local retries="${2:-1}"
    local delay="${3:-5}"
    
    for ((i=1; i<=retries; i++)); do
        log "Executando: $cmd (tentativa $i/$retries)"
        if eval "$cmd" >> "$LOG_FILE" 2>&1; then
            return 0
        else
            if [ $i -lt $retries ]; then
                warn "Falha na tentativa $i, aguardando ${delay}s antes de retry..."
                sleep "$delay"
            fi
        fi
    done
    error "Comando falhou após $retries tentativas: $cmd"
    return 1
}

# Função para corrigir erro automaticamente
fix_error() {
    local error_type="$1"
    log "🔧 Corrigindo erro: $error_type"
    
    case "$error_type" in
        "namespace_invalid_metadata")
            log "Aplicando patch no namespace para metadata Helm..."
            kubectl patch namespace "$NAMESPACE" \
                -p '{"metadata":{"labels":{"app.kubernetes.io/managed-by":"Helm"},"annotations":{"meta.helm.sh/release-name":"'$RELEASE_NAME'","meta.helm.sh/release-namespace":"'$NAMESPACE'"}}}' || true
            ;;
        "ghcr_secret_missing")
            log "Criando secret do GHCR..."
            read -p "Digite o token do GHCR: " GHCR_TOKEN
            kubectl create secret docker-registry ghcr-secret \
                --docker-server=ghcr.io \
                --docker-username=abelisboa \
                --docker-password="$GHCR_TOKEN" \
                --namespace="$NAMESPACE" || \
            kubectl create secret docker-registry ghcr-secret \
                --docker-server=ghcr.io \
                --docker-username=abelisboa \
                --docker-password="$GHCR_TOKEN" \
                --namespace="$NAMESPACE" \
                --dry-run=client -o yaml | kubectl apply -f -
            ;;
        "storageclass_pending")
            log "Verificando e corrigindo StorageClass..."
            if ! kubectl get sc nfs-storage &>/dev/null; then
                log "Instalando NFS provisioner..."
                helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner || true
                helm repo update
                helm upgrade --install nfs-storage nfs-subdir-external-provisioner/nfs-subdir-external-provisioner \
                    -n kube-system \
                    --set nfs.server=192.168.10.16 \
                    --set nfs.path=/srv/nfs/kubedata \
                    --set storageClass.name=nfs-storage \
                    --set storageClass.defaultClass=true
            fi
            ;;
        "imagepull_error")
            log "Verificando secret GHCR e imagens..."
            if ! kubectl get secret ghcr-secret -n "$NAMESPACE" &>/dev/null; then
                fix_error "ghcr_secret_missing"
            fi
            log "Verificando acesso às imagens GHCR..."
            ;;
        "pvc_pending")
            log "Verificando PVCs pendentes..."
            kubectl get pvc -n "$NAMESPACE" | grep Pending | while read -r pvc rest; do
                warn "PVC pendente: $pvc"
                kubectl describe pvc "$pvc" -n "$NAMESPACE" | tee -a "$LOG_FILE"
            done
            ;;
    esac
}

# ============================================
# FASE 0 — PREPARAÇÃO
# ============================================
log "╔════════════════════════════════════════════════════════════╗"
log "║  FASE 0 — PREPARAÇÃO DO AMBIENTE                          ║"
log "╚════════════════════════════════════════════════════════════╝"

log "Verificando conectividade..."
if ! ping -c 1 8.8.8.8 &>/dev/null; then
    error "Sem conectividade de rede"
    exit 1
fi

log "Verificando acesso ao cluster..."
if ! kubectl get nodes -o wide; then
    error "Não foi possível acessar o cluster Kubernetes"
    exit 1
fi

kubectl cluster-info | tee -a "$LOG_FILE"

log "Verificando kubectl-safe..."
if ! which kubectl-safe &>/dev/null; then
    warn "kubectl-safe não encontrado (opcional)"
fi

# ============================================
# FASE 1 — VALIDAR STORAGE (NFS)
# ============================================
log ""
log "╔════════════════════════════════════════════════════════════╗"
log "║  FASE 1 — VALIDAR STORAGE (NFS)                           ║"
log "╚════════════════════════════════════════════════════════════╝"

log "Verificando StorageClass..."
kubectl get storageclass | tee -a "$LOG_FILE"

log "Verificando pods NFS no kube-system..."
kubectl get pods -n kube-system | grep nfs | tee -a "$LOG_FILE"

# Verificar se há StorageClass
if ! kubectl get sc | grep -q .; then
    warn "Nenhum StorageClass encontrado, instalando NFS provisioner..."
    fix_error "storageclass_pending"
fi

# Verificar montagem NFS
log "Verificando montagem NFS..."
if command -v showmount &>/dev/null; then
    showmount -e 192.168.10.16 2>&1 | tee -a "$LOG_FILE" || warn "showmount falhou"
fi

# ============================================
# FASE 2 — VALIDAR E CORRIGIR NAMESPACE
# ============================================
log ""
log "╔════════════════════════════════════════════════════════════╗"
log "║  FASE 2 — VALIDAR E CORRIGIR NAMESPACE                     ║"
log "╚════════════════════════════════════════════════════════════╝"

if ! kubectl get ns "$NAMESPACE" &>/dev/null; then
    log "Criando namespace $NAMESPACE..."
    kubectl create namespace "$NAMESPACE"
else
    log "Namespace $NAMESPACE já existe"
fi

# Aplicar metadata Helm no namespace
log "Aplicando metadata Helm no namespace..."
kubectl patch namespace "$NAMESPACE" \
    -p '{"metadata":{"labels":{"app.kubernetes.io/managed-by":"Helm"},"annotations":{"meta.helm.sh/release-name":"'$RELEASE_NAME'","meta.helm.sh/release-namespace":"'$NAMESPACE'"}}}' || true

# ============================================
# FASE 3 — VALIDAR CHART HELM
# ============================================
log ""
log "╔════════════════════════════════════════════════════════════╗"
log "║  FASE 3 — VALIDAR CHART HELM                              ║"
log "╚════════════════════════════════════════════════════════════╝"

if [ ! -d "$HELM_CHART_PATH" ]; then
    error "Chart Helm não encontrado em: $HELM_CHART_PATH"
    exit 1
fi

log "Verificando estrutura do chart..."
ls -la "$HELM_CHART_PATH" | tee -a "$LOG_FILE"

log "Executando helm lint..."
if ! helm lint "$HELM_CHART_PATH" | tee -a "$LOG_FILE"; then
    error "Helm lint falhou, mas continuando..."
fi

log "Executando helm template (dry-run)..."
helm template "$RELEASE_NAME" "$HELM_CHART_PATH" \
    -f "$VALUES_FILE" \
    -n "$NAMESPACE" \
    --debug 2>&1 | head -100 | tee -a "$LOG_FILE" || warn "Template gerou warnings"

# ============================================
# FASE 4 — VALIDAR VALORES
# ============================================
log ""
log "╔════════════════════════════════════════════════════════════╗"
log "║  FASE 4 — VALIDAR VALORES                                 ║"
log "╚════════════════════════════════════════════════════════════╝"

if [ ! -f "$VALUES_FILE" ]; then
    error "Arquivo values não encontrado: $VALUES_FILE"
    exit 1
fi

log "Verificando arquivo values..."
if ! yq eval . "$VALUES_FILE" &>/dev/null && ! python3 -c "import yaml; yaml.safe_load(open('$VALUES_FILE'))" 2>/dev/null; then
    warn "Não foi possível validar YAML, mas continuando..."
else
    log "Arquivo values válido"
fi

# Verificar se há placeholders
if grep -q "<.*>" "$VALUES_FILE"; then
    warn "Arquivo values contém placeholders não substituídos!"
    grep "<.*>" "$VALUES_FILE" | head -5
fi

# ============================================
# FASE 5 — DEPLOY TRISLA (SEM ATOMIC)
# ============================================
log ""
log "╔════════════════════════════════════════════════════════════╗"
log "║  FASE 5 — DEPLOY TRISLA                                   ║"
log "╚════════════════════════════════════════════════════════════╝"

# Verificar se release já existe
if helm list -n "$NAMESPACE" | grep -q "$RELEASE_NAME"; then
    warn "Release $RELEASE_NAME já existe, fazendo upgrade..."
    ACTION="upgrade"
else
    log "Instalando nova release $RELEASE_NAME..."
    ACTION="install"
fi

log "Executando helm $ACTION com debug e wait..."
helm "$ACTION" "$RELEASE_NAME" "$HELM_CHART_PATH" \
    -n "$NAMESPACE" \
    -f "$VALUES_FILE" \
    --timeout 15m \
    --wait \
    --debug 2>&1 | tee -a "$LOG_FILE" || {
    error "Helm deploy falhou, analisando erros..."
    
    # Verificar eventos
    log "Eventos recentes:"
    kubectl get events -n "$NAMESPACE" --sort-by=.metadata.creationTimestamp | tail -20 | tee -a "$LOG_FILE"
    
    # Tentar corrigir erros comuns
    if kubectl get events -n "$NAMESPACE" | grep -q "secret.*not found"; then
        fix_error "ghcr_secret_missing"
    fi
    
    if kubectl get events -n "$NAMESPACE" | grep -q "invalid ownership metadata"; then
        fix_error "namespace_invalid_metadata"
    fi
    
    # Retry
    warn "Tentando novamente após correções..."
    helm "$ACTION" "$RELEASE_NAME" "$HELM_CHART_PATH" \
        -n "$NAMESPACE" \
        -f "$VALUES_FILE" \
        --timeout 15m \
        --wait \
        --debug 2>&1 | tee -a "$LOG_FILE" || error "Deploy falhou após correções"
}

# ============================================
# FASE 6 — ACOMPANHAMENTO EM TEMPO REAL
# ============================================
log ""
log "╔════════════════════════════════════════════════════════════╗"
log "║  FASE 6 — ACOMPANHAMENTO EM TEMPO REAL                    ║"
log "╚════════════════════════════════════════════════════════════╝"

log "Aguardando pods iniciarem (30s)..."
sleep 30

MAX_ITERATIONS=60
ITERATION=0

while [ $ITERATION -lt $MAX_ITERATIONS ]; do
    ITERATION=$((ITERATION + 1))
    log "Verificação $ITERATION/$MAX_ITERATIONS..."
    
    # Obter status dos pods
    kubectl get pods -n "$NAMESPACE" -o wide | tee -a "$LOG_FILE"
    
    # Verificar pods com problemas
    PROBLEM_PODS=$(kubectl get pods -n "$NAMESPACE" -o json | \
        jq -r '.items[] | select(.status.phase != "Running" and .status.phase != "Succeeded") | "\(.metadata.name) \(.status.phase)"' 2>/dev/null || \
        kubectl get pods -n "$NAMESPACE" | grep -v "Running\|Completed" | awk '{print $1 " " $3}' | grep -v "NAME")
    
    if [ -z "$PROBLEM_PODS" ]; then
        log "✅ Todos os pods estão Running!"
        break
    fi
    
    # Processar cada pod com problema
    echo "$PROBLEM_PODS" | while IFS= read -r line; do
        if [ -z "$line" ]; then continue; fi
        POD_NAME=$(echo "$line" | awk '{print $1}')
        STATUS=$(echo "$line" | awk '{print $2}')
        
        if [ "$POD_NAME" = "NAME" ]; then continue; fi
        
        warn "Pod com problema: $POD_NAME (Status: $STATUS)"
        
        # Descrever pod
        log "Descrevendo pod $POD_NAME..."
        kubectl describe pod "$POD_NAME" -n "$NAMESPACE" | tee -a "$LOG_FILE"
        
        # Logs do pod
        log "Logs do pod $POD_NAME..."
        kubectl logs "$POD_NAME" -n "$NAMESPACE" --all-containers --tail=50 | tee -a "$LOG_FILE" || true
        
        # Corrigir baseado no erro
        case "$STATUS" in
            "Pending"|"ContainerCreating")
                # Verificar eventos
                kubectl get events -n "$NAMESPACE" --field-selector involvedObject.name="$POD_NAME" | tail -5 | tee -a "$LOG_FILE"
                ;;
            "ImagePullBackOff"|"ErrImagePull")
                warn "Erro de pull de imagem em $POD_NAME"
                fix_error "imagepull_error"
                ;;
            "CrashLoopBackOff")
                warn "Pod em CrashLoopBackOff: $POD_NAME"
                log "Últimos logs antes do crash:"
                kubectl logs "$POD_NAME" -n "$NAMESPACE" --all-containers --previous --tail=100 | tee -a "$LOG_FILE" || true
                ;;
        esac
    done
    
    # Verificar PVCs pendentes
    PENDING_PVCS=$(kubectl get pvc -n "$NAMESPACE" | grep Pending | awk '{print $1}' || true)
    if [ -n "$PENDING_PVCS" ]; then
        warn "PVCs pendentes detectados"
        fix_error "pvc_pending"
    fi
    
    sleep 10
done

# ============================================
# FASE 7 — VERIFICAÇÃO FINAL
# ============================================
log ""
log "╔════════════════════════════════════════════════════════════╗"
log "║  FASE 7 — VERIFICAÇÃO FINAL                                ║"
log "╚════════════════════════════════════════════════════════════╝"

log "Status final dos pods:"
kubectl get pods -n "$NAMESPACE" -o wide | tee -a "$LOG_FILE"

log "Status dos serviços:"
kubectl get svc -n "$NAMESPACE" | tee -a "$LOG_FILE"

log "Status dos deployments:"
kubectl get deployments -n "$NAMESPACE" | tee -a "$LOG_FILE"

log "Eventos recentes:"
kubectl get events -n "$NAMESPACE" --sort-by=.metadata.creationTimestamp | tail -30 | tee -a "$LOG_FILE"

# Verificar logs de cada módulo
MODULES=("sem-csmf" "ml-nsmf" "decision-engine" "bc-nssmf" "sla-agent-layer" "nasp-adapter")

log ""
log "Verificando logs de cada módulo..."
for module in "${MODULES[@]}"; do
    POD=$(kubectl get pods -n "$NAMESPACE" -l app="$module" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    if [ -n "$POD" ]; then
        log "Logs de $module ($POD):"
        kubectl logs "$POD" -n "$NAMESPACE" --tail=20 | tee -a "$LOG_FILE" || true
    else
        warn "Pod do módulo $module não encontrado"
    fi
done

# ============================================
# FASE 8 — RELATÓRIO FINAL
# ============================================
log ""
log "╔════════════════════════════════════════════════════════════╗"
log "║  FASE 8 — RELATÓRIO FINAL                                 ║"
log "╚════════════════════════════════════════════════════════════╝"

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

REPORT_FILE="/tmp/trisla-deploy-report-$(date +%Y%m%d-%H%M%S).md"

cat > "$REPORT_FILE" <<EOF
# Relatório de Deploy TriSLA v3.4.0 - NASP

**Data:** $(date)
**Duração:** ${MINUTES}m ${SECONDS}s
**Release:** $RELEASE_NAME
**Namespace:** $NAMESPACE

---

## Status do Deploy

EOF

# Contar pods por status
RUNNING_PODS=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | grep -c "Running" || echo "0")
TOTAL_PODS=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l || echo "0")

if [ "$RUNNING_PODS" -eq "$TOTAL_PODS" ] && [ "$TOTAL_PODS" -gt 0 ]; then
    echo "✅ **SUCESSO** - Todos os pods estão Running" >> "$REPORT_FILE"
    SUCCESS=true
else
    echo "⚠️ **PARCIAL** - Alguns pods não estão Running" >> "$REPORT_FILE"
    SUCCESS=false
fi

cat >> "$REPORT_FILE" <<EOF

**Pods Running:** $RUNNING_PODS / $TOTAL_PODS

---

## Serviços em Execução

\`\`\`
$(kubectl get svc -n "$NAMESPACE" 2>/dev/null || echo "Nenhum serviço encontrado")
\`\`\`

---

## Deployments

\`\`\`
$(kubectl get deployments -n "$NAMESPACE" 2>/dev/null || echo "Nenhum deployment encontrado")
\`\`\`

---

## Problemas Detectados e Corrigidos

EOF

# Adicionar problemas do log
if grep -q "Corrigindo erro" "$LOG_FILE"; then
    grep "Corrigindo erro" "$LOG_FILE" | sed 's/^/- /' >> "$REPORT_FILE"
else
    echo "- Nenhum problema detectado que requeira correção automática" >> "$REPORT_FILE"
fi

cat >> "$REPORT_FILE" <<EOF

---

## Próximos Passos Recomendados

1. Verificar health checks de cada módulo:
   \`\`\`bash
   kubectl get pods -n $NAMESPACE -o wide
   \`\`\`

2. Verificar logs de módulos específicos:
   \`\`\`bash
   kubectl logs -n $NAMESPACE -l app=sem-csmf --tail=50
   kubectl logs -n $NAMESPACE -l app=decision-engine --tail=50
   \`\`\`

3. Testar interfaces:
   - I-02 (SEM-CSMF): \`curl http://<SEM_CSMF_SERVICE>:8080/health\`
   - I-01 (Decision Engine gRPC): \`grpcurl -plaintext <SERVICE>:50051 list\`
   - I-07 (NASP-Adapter): \`curl http://<NASP_ADAPTER_SERVICE>:8085/health\`

4. Verificar métricas no Prometheus:
   \`\`\`bash
   kubectl port-forward -n monitoring svc/prometheus 9090:9090
   \`\`\`

5. Acessar Grafana:
   \`\`\`bash
   kubectl port-forward -n monitoring svc/grafana 3000:3000
   \`\`\`

---

## Log Completo

O log completo está disponível em: \`$LOG_FILE\`

EOF

log "Relatório gerado em: $REPORT_FILE"
cat "$REPORT_FILE"

if [ "$SUCCESS" = true ]; then
    log ""
    log "╔════════════════════════════════════════════════════════════╗"
    log "║  ✅ DEPLOY CONCLUÍDO COM SUCESSO                          ║"
    log "╚════════════════════════════════════════════════════════════╝"
    exit 0
else
    log ""
    log "╔════════════════════════════════════════════════════════════╗"
    log "║  ⚠️  DEPLOY CONCLUÍDO COM AVISOS                          ║"
    log "╚════════════════════════════════════════════════════════════╝"
    log "Verifique o relatório em: $REPORT_FILE"
    exit 1
fi

