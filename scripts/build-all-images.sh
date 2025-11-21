#!/bin/bash
# ============================================
# Script para Build e Push de Todas as Imagens
# ============================================
# Build e push de todas as imagens Docker para GHCR
# ============================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configurações
REGISTRY="ghcr.io"
USERNAME="${GHCR_USER:-abelisboa}"
IMAGE_PREFIX="trisla"

# Verificar se está logado
if ! docker info | grep -q "Username"; then
    echo -e "${YELLOW}⚠️  Não está logado no Docker. Fazendo login...${NC}"
    if [ -z "$GHCR_TOKEN" ]; then
        echo -e "${RED}❌ Erro: GHCR_TOKEN não configurado${NC}"
        echo "Execute: export GHCR_TOKEN=seu_token"
        exit 1
    fi
    echo "$GHCR_TOKEN" | docker login "$REGISTRY" -u "$USERNAME" --password-stdin
fi

echo -e "${GREEN}🚀 Iniciando build e push de todas as imagens...${NC}"
echo ""

# Lista de serviços
SERVICES=(
    "sem-csmf"
    "ml-nsmf"
    "decision-engine"
    "bc-nssmf"
    "sla-agent-layer"
    "nasp-adapter"
    "ui-dashboard"
)

# Build e push de cada serviço
for service in "${SERVICES[@]}"; do
    echo -e "${YELLOW}📦 Buildando ${service}...${NC}"
    
    cd "apps/${service}"
    
    # Build
    IMAGE_NAME="${REGISTRY}/${USERNAME}/${IMAGE_PREFIX}-${service}:latest"
    docker build -t "$IMAGE_NAME" .
    
    # Push
    echo -e "${YELLOW}⬆️  Fazendo push de ${IMAGE_NAME}...${NC}"
    docker push "$IMAGE_NAME"
    
    echo -e "${GREEN}✅ ${service} concluído!${NC}"
    echo ""
    
    cd ../..
done

echo -e "${GREEN}🎉 Todas as imagens foram buildadas e enviadas para GHCR!${NC}"
echo ""
echo "📋 Imagens criadas:"
for service in "${SERVICES[@]}"; do
    echo "   - ${REGISTRY}/${USERNAME}/${IMAGE_PREFIX}-${service}:latest"
done
echo ""
echo "🔗 Verificar em: https://github.com/${USERNAME}/TriSLA/pkgs/container"

