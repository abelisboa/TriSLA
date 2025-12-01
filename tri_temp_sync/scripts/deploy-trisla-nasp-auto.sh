#!/bin/bash
# ============================================
# Script Automático: Deploy TriSLA no NASP
# ============================================
# Deploy completo e automatizado do TriSLA no ambiente NASP
# ============================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     TriSLA - Deploy Automático no NASP (Local)            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar se está no diretório correto
if [ ! -f "README.md" ] || [ ! -d "helm" ] || [ ! -d "scripts" ]; then
    echo -e "${RED}❌ Erro: Execute este script no diretório raiz do projeto TriSLA${NC}"
    echo "   cd ~/gtp5g/trisla"
    exit 1
fi

# Verificar se está no NASP
if ! kubectl cluster-info &>/dev/null; then
    echo -e "${RED}❌ Erro: Não está conectado ao cluster Kubernetes${NC}"
    echo "   Execute este script no node1 do NASP"
    exit 1
fi

NAMESPACE="trisla"
RELEASE_NAME="trisla"
VALUES_FILE="helm/trisla/values-nasp.yaml"

echo -e "${YELLOW}📋 Configuração:${NC}"
echo "   Namespace: $NAMESPACE"
echo "   Release: $RELEASE_NAME"
echo "   Values: $VALUES_FILE"
echo ""

# FASE 1: Preparação
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}FASE 1: Preparação do Ambiente${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -f "scripts/prepare-nasp-deploy.sh" ]; then
    echo -e "${YELLOW}🔧 Executando preparação...${NC}"
    bash scripts/prepare-nasp-deploy.sh
else
    echo -e "${YELLOW}⚠️  Script de preparação não encontrado, executando manualmente...${NC}"
    
    # Criar namespace
    echo -e "${YELLOW}📁 Criando namespace...${NC}"
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # Criar secret do GHCR (se token fornecido)
    if [ -n "${GHCR_TOKEN:-}" ]; then
        echo -e "${YELLOW}🔐 Criando secret do GHCR...${NC}"
        kubectl create secret docker-registry ghcr-secret \
            --docker-server=ghcr.io \
            --docker-username="${GHCR_USER:-abelisboa}" \
            --docker-password="$GHCR_TOKEN" \
            --docker-email="${GHCR_USER:-abelisboa}@gmail.com" \
            -n "$NAMESPACE" \
            --dry-run=client -o yaml | kubectl apply -f -
    else
        echo -e "${YELLOW}⚠️  GHCR_TOKEN não configurado. Configure antes do deploy:${NC}"
        echo "   export GHCR_TOKEN=seu_token"
        echo "   export GHCR_USER=seu_usuario"
    fi
fi

echo ""

# FASE 2: Validação do Helm Chart
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}FASE 2: Validação do Helm Chart${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ ! -f "$VALUES_FILE" ]; then
    echo -e "${RED}❌ Erro: $VALUES_FILE não encontrado${NC}"
    echo "   Execute: ./scripts/fill_values_production.sh"
    exit 1
fi

echo -e "${YELLOW}🔍 Validando Helm chart...${NC}"
helm lint ./helm/trisla -f "$VALUES_FILE"
echo -e "${GREEN}✅ Helm chart válido${NC}"
echo ""

# FASE 3: Deploy
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}FASE 3: Deploy do TriSLA${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}🚀 Iniciando deploy...${NC}"
echo ""

helm upgrade --install "$RELEASE_NAME" "./helm/trisla" \
    --namespace "$NAMESPACE" \
    --create-namespace \
    --values "$VALUES_FILE" \
    --set production.enabled=true \
    --set production.simulationMode=false \
    --set production.useRealServices=true \
    --set production.executeRealActions=true \
    --wait \
    --timeout 15m

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Deploy concluído com sucesso!${NC}"
else
    echo ""
    echo -e "${RED}❌ Erro no deploy. Verifique os logs acima.${NC}"
    exit 1
fi

echo ""

# FASE 4: Validação
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}FASE 4: Validação do Deploy${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}📊 Status dos Pods:${NC}"
kubectl get pods -n "$NAMESPACE"
echo ""

echo -e "${YELLOW}📊 Status dos Services:${NC}"
kubectl get svc -n "$NAMESPACE"
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Deploy Automático - CONCLUÍDO!               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "📋 Comandos úteis:"
echo "   - Ver pods: kubectl get pods -n $NAMESPACE"
echo "   - Ver logs: kubectl logs -n $NAMESPACE <pod-name>"
echo "   - Ver serviços: kubectl get svc -n $NAMESPACE"
echo "   - Ver eventos: kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp'"
echo ""

