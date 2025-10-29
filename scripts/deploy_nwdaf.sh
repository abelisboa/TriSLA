#!/bin/bash

# Deploy do NWDAF no Kubernetes
# Este script faz o deploy completo do NWDAF usando Helm

set -e

echo "🚀 Iniciando deploy do NWDAF no Kubernetes..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar se kubectl está disponível
if ! command -v kubectl &> /dev/null; then
    error "kubectl não encontrado. Instale o kubectl primeiro."
    exit 1
fi

# Verificar se helm está disponível
if ! command -v helm &> /dev/null; then
    error "helm não encontrado. Instale o helm primeiro."
    exit 1
fi

# Verificar se o namespace existe
log "Verificando namespace trisla..."
if ! kubectl get namespace trisla &> /dev/null; then
    log "Criando namespace trisla..."
    kubectl create namespace trisla
    success "Namespace trisla criado"
else
    success "Namespace trisla já existe"
fi

# Verificar se o cluster está acessível
log "Verificando conectividade com o cluster..."
if ! kubectl get nodes &> /dev/null; then
    error "Não é possível conectar ao cluster Kubernetes"
    error "Verifique se o túnel SSH está ativo e se as credenciais estão corretas"
    exit 1
fi

success "Cluster Kubernetes acessível"

# Construir imagem Docker do NWDAF
log "Construindo imagem Docker do NWDAF..."
if [ -f "apps/nwdaf/Dockerfile" ]; then
    docker build -t ghcr.io/abelisboa/trisla-nwdaf:latest apps/nwdaf/
    success "Imagem Docker construída"
else
    error "Dockerfile do NWDAF não encontrado"
    exit 1
fi

# Fazer push da imagem para o registry
log "Fazendo push da imagem para o registry..."
docker push ghcr.io/abelisboa/trisla-nwdaf:latest
success "Imagem enviada para o registry"

# Verificar se o Helm chart existe
log "Verificando Helm chart do NWDAF..."
if [ -d "helm/nwdaf" ]; then
    success "Helm chart encontrado"
else
    error "Helm chart do NWDAF não encontrado"
    exit 1
fi

# Instalar/atualizar o NWDAF
log "Instalando NWDAF com Helm..."
helm upgrade --install nwdaf helm/nwdaf \
    --namespace trisla \
    --set image.repository=ghcr.io/abelisboa/trisla-nwdaf \
    --set image.tag=latest \
    --set image.pullPolicy=Always \
    --wait \
    --timeout=300s

if [ $? -eq 0 ]; then
    success "NWDAF instalado com sucesso"
else
    error "Falha ao instalar NWDAF"
    exit 1
fi

# Verificar status do deployment
log "Verificando status do deployment..."
kubectl get deployment nwdaf -n trisla

# Aguardar pods estarem prontos
log "Aguardando pods estarem prontos..."
kubectl wait --for=condition=available --timeout=300s deployment/nwdaf -n trisla

# Verificar pods
log "Verificando pods do NWDAF..."
kubectl get pods -l app.kubernetes.io/name=nwdaf -n trisla

# Verificar logs
log "Verificando logs do NWDAF..."
kubectl logs -l app.kubernetes.io/name=nwdaf -n trisla --tail=20

# Verificar serviços
log "Verificando serviços do NWDAF..."
kubectl get svc -l app.kubernetes.io/name=nwdaf -n trisla

# Testar conectividade
log "Testando conectividade do NWDAF..."
NWDAF_POD=$(kubectl get pods -l app.kubernetes.io/name=nwdaf -n trisla -o jsonpath='{.items[0].metadata.name}')

if [ -n "$NWDAF_POD" ]; then
    # Testar health check
    log "Testando health check..."
    if kubectl exec $NWDAF_POD -n trisla -- curl -f http://localhost:8080/health &> /dev/null; then
        success "Health check passou"
    else
        warning "Health check falhou"
    fi
    
    # Testar readiness check
    log "Testando readiness check..."
    if kubectl exec $NWDAF_POD -n trisla -- curl -f http://localhost:8080/ready &> /dev/null; then
        success "Readiness check passou"
    else
        warning "Readiness check falhou"
    fi
else
    error "Pod do NWDAF não encontrado"
fi

# Verificar métricas do Prometheus
log "Verificando ServiceMonitor do NWDAF..."
if kubectl get servicemonitor nwdaf -n trisla &> /dev/null; then
    success "ServiceMonitor do NWDAF encontrado"
else
    warning "ServiceMonitor do NWDAF não encontrado"
fi

# Resumo do deploy
echo ""
echo "=========================================="
echo "📊 RESUMO DO DEPLOY DO NWDAF"
echo "=========================================="

# Verificar status do deployment
if kubectl get deployment nwdaf -n trisla -o jsonpath='{.status.readyReplicas}' | grep -q "1"; then
    success "Deployment: PRONTO"
else
    error "Deployment: FALHOU"
fi

# Verificar pods
POD_COUNT=$(kubectl get pods -l app.kubernetes.io/name=nwdaf -n trisla --no-headers | wc -l)
if [ $POD_COUNT -gt 0 ]; then
    success "Pods: $POD_COUNT encontrados"
else
    error "Pods: Nenhum encontrado"
fi

# Verificar serviços
SVC_COUNT=$(kubectl get svc -l app.kubernetes.io/name=nwdaf -n trisla --no-headers | wc -l)
if [ $SVC_COUNT -gt 0 ]; then
    success "Serviços: $SVC_COUNT encontrados"
else
    error "Serviços: Nenhum encontrado"
fi

echo ""
echo "🎉 DEPLOY DO NWDAF CONCLUÍDO!"
echo "✅ O NWDAF está rodando no Kubernetes"
echo "✅ Pronto para integração com outros módulos TriSLA"
echo "✅ Pronto para configuração de dashboards no Grafana"

# Próximos passos
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Executar: ./scripts/test_nwdaf.sh"
echo "2. Configurar integração com outros módulos"
echo "3. Configurar dashboards no Grafana"
echo "4. Continuar para a Fase 6 da implementação"
