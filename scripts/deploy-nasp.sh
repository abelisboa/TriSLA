#!/bin/bash
set -e

# ============================================
# Script de Deploy no NASP - TriSLA
# ============================================

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "=========================================="
echo "🚀 Deploy TriSLA no NASP"
echo "=========================================="
echo ""

# Verificar se está no node1
if [ ! -d "/home/porvir5g/gtp5g/trisla" ]; then
    echo -e "${RED}❌ Diretório TriSLA não encontrado${NC}"
    echo "   Execute: cd /home/porvir5g/gtp5g/trisla"
    exit 1
fi

cd /home/porvir5g/gtp5g/trisla

# Atualizar código
echo -e "${CYAN}📥 Atualizando código do GitHub...${NC}"
git pull origin main

# Verificar se GHCR_TOKEN está definido
if [ -z "$GHCR_TOKEN" ]; then
    echo -e "${YELLOW}⚠️  GHCR_TOKEN não definido${NC}"
    echo "   Exporte: export GHCR_TOKEN='seu_token'"
    exit 1
fi

# Login no GHCR
echo -e "${CYAN}🔐 Fazendo login no GHCR...${NC}"
echo "$GHCR_TOKEN" | docker login ghcr.io -u abelisboa --password-stdin

# Deploy com Helm
echo -e "${CYAN}📦 Fazendo deploy com Helm...${NC}"
helm upgrade --install trisla ./helm/trisla \
    -f ./helm/trisla/values-nasp.yaml \
    --namespace trisla \
    --create-namespace

# Aguardar pods ficarem prontos
echo -e "${CYAN}⏳ Aguardando pods ficarem prontos...${NC}"
kubectl wait --for=condition=Ready pod -l app.kubernetes.io/name=trisla -n trisla --timeout=300s || true

# Mostrar status
echo ""
echo -e "${CYAN}📊 Status dos pods:${NC}"
kubectl get pods -n trisla

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Deploy concluído${NC}"
echo "=========================================="











