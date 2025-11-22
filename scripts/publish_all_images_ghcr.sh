#!/usr/bin/env bash
# ============================================
# Script de Publicação de Imagens GHCR - TriSLA
# ============================================
# Constrói e publica todas as imagens Docker dos módulos TriSLA
# no GitHub Container Registry (GHCR)
# ============================================
# Uso: GHCR_TOKEN=<token> ./scripts/publish_all_images_ghcr.sh
# ============================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GHCR_USER="abelisboa"
GHCR_REGISTRY="ghcr.io"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}🚀 Publicação de Imagens TriSLA no GHCR${NC}"
echo -e "${BLUE}============================================================${NC}\n"

# ============================================
# 1. Verificar Pré-requisitos
# ============================================

echo -e "${BLUE}1️⃣ Verificando pré-requisitos...${NC}\n"

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker não encontrado. Por favor, instale Docker.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker encontrado${NC}"

# Verificar GHCR_TOKEN
if [ -z "${GHCR_TOKEN:-}" ]; then
    echo -e "${RED}❌ GHCR_TOKEN não definido.${NC}"
    echo "   Defina a variável: export GHCR_TOKEN=<seu_token>"
    echo "   Ou execute: GHCR_TOKEN=<token> $0"
    exit 1
fi
echo -e "${GREEN}✅ GHCR_TOKEN definido${NC}"

# Verificar se está na pasta raiz
if [ ! -f "$PROJECT_ROOT/docker-compose.yml" ]; then
    echo -e "${RED}❌ Não está na pasta raiz do projeto.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Pasta raiz do projeto confirmada${NC}\n"

# ============================================
# 2. Login no GHCR
# ============================================

echo -e "${BLUE}2️⃣ Fazendo login no GHCR...${NC}\n"

if echo "$GHCR_TOKEN" | docker login "$GHCR_REGISTRY" -u "$GHCR_USER" --password-stdin; then
    echo -e "${GREEN}✅ Login no GHCR realizado com sucesso${NC}\n"
else
    echo -e "${RED}❌ Falha no login no GHCR. Verifique o token.${NC}"
    exit 1
fi

# ============================================
# 3. Lista de Módulos
# ============================================

MODULES=(
    "sem-csmf"
    "ml-nsmf"
    "decision-engine"
    "bc-nssmf"
    "sla-agent-layer"
    "nasp-adapter"
    "ui-dashboard"
)

echo -e "${BLUE}3️⃣ Módulos a serem publicados:${NC}"
for module in "${MODULES[@]}"; do
    echo "   - $module"
done
echo ""

# ============================================
# 4. Construir e Publicar Imagens
# ============================================

SUCCESS_COUNT=0
FAILED_COUNT=0
FAILED_MODULES=()

for MODULE in "${MODULES[@]}"; do
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}📦 Construindo e publicando: $MODULE${NC}"
    echo -e "${BLUE}============================================================${NC}\n"
    
    MODULE_DIR="$PROJECT_ROOT/apps/$MODULE"
    DOCKERFILE="$MODULE_DIR/Dockerfile"
    IMAGE_NAME="ghcr.io/$GHCR_USER/trisla-$MODULE:latest"
    
    # Verificar se Dockerfile existe
    if [ ! -f "$DOCKERFILE" ]; then
        echo -e "${RED}❌ Dockerfile não encontrado: $DOCKERFILE${NC}"
        FAILED_COUNT=$((FAILED_COUNT + 1))
        FAILED_MODULES+=("$MODULE")
        continue
    fi
    
    # Verificar se diretório do módulo existe
    if [ ! -d "$MODULE_DIR" ]; then
        echo -e "${RED}❌ Diretório do módulo não encontrado: $MODULE_DIR${NC}"
        FAILED_COUNT=$((FAILED_COUNT + 1))
        FAILED_MODULES+=("$MODULE")
        continue
    fi
    
    echo -e "${YELLOW}📋 Dockerfile: $DOCKERFILE${NC}"
    echo -e "${YELLOW}📋 Imagem: $IMAGE_NAME${NC}"
    echo -e "${YELLOW}📋 Contexto: $MODULE_DIR${NC}\n"
    
    # Construir e publicar
    if docker buildx build \
        -t "$IMAGE_NAME" \
        -f "$DOCKERFILE" \
        --platform linux/amd64 \
        --push \
        "$MODULE_DIR" 2>&1; then
        
        echo -e "${GREEN}✅ Imagem $MODULE publicada com sucesso${NC}\n"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        
        # Obter digest da imagem
        DIGEST=$(docker inspect "$IMAGE_NAME" --format='{{index .RepoDigests 0}}' 2>/dev/null || echo "N/A")
        if [ "$DIGEST" != "N/A" ]; then
            echo -e "${GREEN}   Digest: $DIGEST${NC}\n"
        fi
    else
        echo -e "${RED}❌ Falha ao publicar imagem $MODULE${NC}\n"
        FAILED_COUNT=$((FAILED_COUNT + 1))
        FAILED_MODULES+=("$MODULE")
    fi
done

# ============================================
# 5. Resumo da Publicação
# ============================================

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}📊 Resumo da Publicação${NC}"
echo -e "${BLUE}============================================================${NC}\n"

echo -e "${GREEN}✅ Imagens publicadas com sucesso: $SUCCESS_COUNT${NC}"

if [ $FAILED_COUNT -gt 0 ]; then
    echo -e "${RED}❌ Imagens com falha: $FAILED_COUNT${NC}"
    echo -e "${RED}   Módulos com falha:${NC}"
    for module in "${FAILED_MODULES[@]}"; do
        echo -e "${RED}     - $module${NC}"
    done
    echo ""
fi

# ============================================
# 6. Validar Imagens Após Push
# ============================================

echo -e "${BLUE}6️⃣ Validando imagens publicadas...${NC}\n"

if [ -f "$SCRIPT_DIR/audit_ghcr_images.py" ]; then
    if python3 "$SCRIPT_DIR/audit_ghcr_images.py"; then
        echo -e "${GREEN}✅ Auditoria concluída${NC}\n"
    else
        echo -e "${YELLOW}⚠️ Auditoria concluída com avisos${NC}\n"
    fi
else
    echo -e "${YELLOW}⚠️ Script de auditoria não encontrado: scripts/audit_ghcr_images.py${NC}\n"
fi

# ============================================
# 7. Mensagem Final
# ============================================

echo -e "${BLUE}============================================================${NC}"
if [ $FAILED_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ FINALIZADO — Todas as imagens foram publicadas no GHCR${NC}"
else
    echo -e "${YELLOW}⚠️ FINALIZADO — $SUCCESS_COUNT imagens publicadas, $FAILED_COUNT falhas${NC}"
fi
echo -e "${BLUE}============================================================${NC}\n"

echo -e "${BLUE}📋 Próximos passos:${NC}"
echo "   1. Verificar docs/IMAGES_GHCR_MATRIX.md para confirmação"
echo "   2. Testar pull das imagens: docker pull ghcr.io/$GHCR_USER/trisla-<module>:latest"
echo "   3. Configurar secret GHCR no Kubernetes (se ainda não feito)"
echo ""

if [ $FAILED_COUNT -gt 0 ]; then
    exit 1
else
    exit 0
fi


