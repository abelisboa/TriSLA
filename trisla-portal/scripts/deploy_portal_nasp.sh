#!/bin/bash
# Script para deploy do Portal TriSLA no cluster NASP

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HELM_CHART_DIR="$PROJECT_ROOT/helm/trisla-portal"

echo "🚀 Deploying Portal TriSLA to NASP cluster..."
echo "Helm chart directory: $HELM_CHART_DIR"

# Verificar se o diretório do Helm chart existe
if [ ! -d "$HELM_CHART_DIR" ]; then
    echo "❌ Erro: Diretório do Helm chart não encontrado: $HELM_CHART_DIR"
    exit 1
fi

# Verificar se helm está instalado
if ! command -v helm &> /dev/null; then
    echo "❌ Erro: Helm não está instalado"
    echo "💡 Instale o Helm: https://helm.sh/docs/intro/install/"
    exit 1
fi

# Verificar conexão com o cluster Kubernetes
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Erro: Não é possível conectar ao cluster Kubernetes"
    echo "💡 Verifique sua configuração do kubectl"
    exit 1
fi

cd "$PROJECT_ROOT"

echo "📦 Installing/Upgrading trisla-portal..."
helm upgrade --install trisla-portal ./helm/trisla-portal \
  -n trisla \
  --create-namespace \
  --wait

echo "✅ Portal TriSLA deployed successfully!"
echo ""
echo "📊 Para verificar o status:"
echo "   kubectl get pods -n trisla -l app=trisla-portal-backend"
echo "   kubectl get pods -n trisla -l app=trisla-portal-frontend"
echo ""
echo "🌐 Para acessar via túnel SSH, execute:"
echo "   ./scripts/create_tunnel.sh"

