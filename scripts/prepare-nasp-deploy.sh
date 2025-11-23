#!/bin/bash
# ============================================
# Script para Preparar Deploy no NASP
# ============================================
# Prepara o ambiente NASP para deploy do TriSLA
# ============================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔧 Preparando ambiente NASP para deploy...${NC}"
echo ""

# Verificar se está no NASP
if ! kubectl cluster-info &>/dev/null; then
    echo -e "${RED}❌ Erro: Não está conectado ao cluster Kubernetes${NC}"
    echo "Execute este script no NASP (node1)"
    exit 1
fi

NAMESPACE="trisla"
GHCR_USER="${GHCR_USER:-abelisboa}"
GHCR_TOKEN="${GHCR_TOKEN}"

# 1. Criar namespace se não existir
echo -e "${YELLOW}📁 Criando namespace ${NAMESPACE}...${NC}"
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✅ Namespace criado${NC}"
echo ""

# 2. Criar secret do GHCR
if [ -z "$GHCR_TOKEN" ]; then
    echo -e "${YELLOW}⚠️  GHCR_TOKEN não configurado${NC}"
    echo "Execute: export GHCR_TOKEN=seu_token"
    echo ""
    read -p "Deseja continuar sem criar o secret? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
else
    echo -e "${YELLOW}🔐 Criando secret do GHCR...${NC}"
    kubectl create secret docker-registry ghcr-secret \
        --docker-server=ghcr.io \
        --docker-username="$GHCR_USER" \
        --docker-password="$GHCR_TOKEN" \
        --docker-email="${GHCR_USER}@gmail.com" \
        -n "$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    echo -e "${GREEN}✅ Secret criado${NC}"
    echo ""
fi

# 3. Validar Helm chart
if [ -d "helm/trisla" ]; then
    echo -e "${YELLOW}🔍 Validando Helm chart...${NC}"
    helm lint ./helm/trisla
    echo -e "${GREEN}✅ Helm chart válido${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠️  Diretório helm/trisla não encontrado${NC}"
    echo "Certifique-se de estar no diretório correto"
fi

# 4. Verificar valores NASP
VALUES_FILE="helm/trisla/values-nasp.yaml"
if [ -f "$VALUES_FILE" ]; then
    echo -e "${YELLOW}📋 Verificando $VALUES_FILE...${NC}"
    
    # Verificar se há placeholders não substituídos
    if grep -q "<.*>" "$VALUES_FILE"; then
        echo -e "${YELLOW}⚠️  Atenção: $VALUES_FILE contém placeholders não substituídos${NC}"
        echo "   Execute scripts/discover-nasp-endpoints.sh para descobrir endpoints"
    else
        echo -e "${GREEN}✅ Arquivo values-nasp.yaml parece estar configurado${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  $VALUES_FILE não encontrado${NC}"
    echo "   Para deploy NASP, este arquivo é obrigatório"
    echo "   Você pode copiar de docs/nasp/values-nasp.yaml como template"
fi

echo ""
echo -e "${GREEN}✅ Preparação concluída!${NC}"
echo ""
echo "📋 Próximos passos:"
echo "   1. Preencher helm/trisla/values-nasp.yaml com valores reais do NASP"
echo "   2. Validar Helm chart: helm lint ./helm/trisla"
echo "   3. Dry-run: helm template trisla-portal ./helm/trisla --values ./helm/trisla/values-nasp.yaml"
echo "   4. Deploy: helm upgrade --install trisla-portal ./helm/trisla --namespace $NAMESPACE --values ./helm/trisla/values-nasp.yaml --wait"

