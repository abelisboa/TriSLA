#!/usr/bin/env bash
# Script para deploy do módulo BESU no NASP - TriSLA
# Uso: ./scripts/deploy-besu-nasp.sh

set -e
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 [TriSLA] Deploy do módulo BESU no NASP"
echo "=========================================="

# Verificar pré-requisitos
echo "📋 [TriSLA] Verificando pré-requisitos..."

if ! command -v kubectl &> /dev/null; then
    echo "❌ ERRO: kubectl não está instalado"
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo "❌ ERRO: helm não está instalado"
    exit 1
fi

# Verificar acesso ao cluster
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ ERRO: Não há acesso ao cluster Kubernetes"
    exit 1
fi

echo "✅ [TriSLA] Pré-requisitos OK"

# Verificar namespace
NAMESPACE="trisla"
echo "📋 [TriSLA] Verificando namespace '$NAMESPACE'..."
if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
    echo "⚠️  [TriSLA] Namespace '$NAMESPACE' não existe. Criando..."
    kubectl create namespace "$NAMESPACE"
fi

# Validar Helm chart
echo "📋 [TriSLA] Validando Helm chart..."
cd "$REPO_ROOT"
helm lint ./helm/trisla || {
    echo "❌ ERRO: Helm chart inválido"
    exit 1
}

# Renderizar templates
echo "📋 [TriSLA] Renderizando templates..."
helm template trisla ./helm/trisla \
    -f ./helm/trisla/values-nasp.yaml \
    --debug > /dev/null || {
    echo "❌ ERRO: Falha ao renderizar templates"
    exit 1
}

echo "✅ [TriSLA] Helm chart válido"

# Aplicar deploy
echo "🚀 [TriSLA] Aplicando deploy do BESU..."
helm upgrade --install trisla ./helm/trisla \
    -n "$NAMESPACE" \
    -f ./helm/trisla/values-nasp.yaml \
    --set besu.enabled=true \
    --set global.bcEnabled=true \
    --cleanup-on-fail \
    --wait \
    --timeout 10m \
    --debug

echo "✅ [TriSLA] Deploy aplicado"

# Aguardar pods ficarem prontos
echo "⏳ [TriSLA] Aguardando pods do BESU ficarem prontos..."
kubectl wait --for=condition=ready pod \
    -l app.kubernetes.io/component=besu \
    -n "$NAMESPACE" \
    --timeout=5m || {
    echo "⚠️  [TriSLA] Timeout aguardando pods. Verificando status..."
    kubectl -n "$NAMESPACE" get pods -l app.kubernetes.io/component=besu
}

# Verificar status
echo "📊 [TriSLA] Verificando status do deploy..."
kubectl -n "$NAMESPACE" get pods -l app.kubernetes.io/component=besu
kubectl -n "$NAMESPACE" get svc -l app.kubernetes.io/component=besu
kubectl -n "$NAMESPACE" get pvc -l app.kubernetes.io/component=besu

# Verificar logs
echo "📋 [TriSLA] Últimas linhas dos logs do BESU:"
kubectl -n "$NAMESPACE" logs -l app.kubernetes.io/component=besu --tail=20 || true

# Testar RPC (se port-forward disponível)
echo "🔍 [TriSLA] Para testar RPC, execute:"
echo "   kubectl -n $NAMESPACE port-forward svc/trisla-besu 8545:8545"
echo "   curl -X POST http://localhost:8545 \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"jsonrpc\":\"2.0\",\"method\":\"web3_clientVersion\",\"id\":1}'"

# Verificar integração BC-NSSMF
echo "🔍 [TriSLA] Verificando integração BC-NSSMF..."
BC_POD=$(kubectl -n "$NAMESPACE" get pods -l app.kubernetes.io/component=bc-nssmf -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
if [ -n "$BC_POD" ]; then
    echo "📋 [TriSLA] Variáveis de ambiente do BC-NSSMF:"
    kubectl -n "$NAMESPACE" exec "$BC_POD" -- env | grep -E "RPC_URL|BC_ENABLED|CHAIN_ID" || true
else
    echo "⚠️  [TriSLA] Pod do BC-NSSMF não encontrado"
fi

echo "✅ [TriSLA] Deploy do BESU concluído!"
echo "📋 [TriSLA] Para mais informações, consulte: besu/DEPLOY_NASP.md"

