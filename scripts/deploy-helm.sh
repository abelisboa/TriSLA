#!/usr/bin/env bash
# ============================================================
# Deploy Helm - TriSLA Dashboard v3.2.4
# Deploy no Kubernetes via Helm
# ============================================================

set -e

NAMESPACE="trisla"
CHART_DIR="./helm/trisla-dashboard"

echo "======================================================"
echo "🚀 Deploy Helm - TriSLA Dashboard v3.2.4"
echo "======================================================"
echo ""

# Verificar se Helm está instalado
if ! command -v helm &> /dev/null; then
    echo "❌ Helm não está instalado"
    echo "   Instale: https://helm.sh/docs/intro/install/"
    exit 1
fi

# Verificar se kubectl está disponível
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl não está instalado"
    exit 1
fi

# Verificar conexão com cluster
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Não é possível conectar ao cluster Kubernetes"
    exit 1
fi

echo "✅ Prerequisites OK"
echo ""

# Criar namespace se não existir
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
    echo "📦 Criando namespace: $NAMESPACE"
    kubectl create namespace $NAMESPACE
fi

# Verificar se o chart já está instalado
if helm list -n $NAMESPACE | grep -q "trisla-dashboard"; then
    echo "🔄 Atualizando deployment existente..."
    helm upgrade trisla-dashboard $CHART_DIR \
        --namespace $NAMESPACE \
        --wait \
        --timeout 5m
else
    echo "📦 Instalando novo deployment..."
    helm install trisla-dashboard $CHART_DIR \
        --namespace $NAMESPACE \
        --create-namespace \
        --wait \
        --timeout 5m
fi

echo ""
echo "✅ Deploy concluído!"
echo ""

# Mostrar status
echo "======================================================"
echo "📊 Status do Deployment"
echo "======================================================"
echo ""
kubectl get pods -n $NAMESPACE -l app=trisla-dashboard
echo ""
kubectl get services -n $NAMESPACE -l app=trisla-dashboard
echo ""
echo "Para verificar logs:"
echo "  kubectl logs -n $NAMESPACE -l app=trisla-dashboard -c backend --tail=50"
echo "  kubectl logs -n $NAMESPACE -l app=trisla-dashboard -c frontend --tail=50"
echo ""
echo "Para port-forward:"
echo "  kubectl port-forward -n $NAMESPACE svc/trisla-dashboard 5000:5000 5174:5174"
echo ""
