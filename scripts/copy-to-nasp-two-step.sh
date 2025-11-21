#!/bin/bash
# ============================================
# Script para Copiar Projeto para NASP (Duas Etapas)
# ============================================
# Copia o projeto completo para NASP via ppgca → node006
# ============================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}📦 Copiando projeto TriSLA para NASP...${NC}"
echo ""

# Configurações
LOCAL_DIR="."
REMOTE_USER="porvir5g"
PPGCA_HOST="ppgca.unisinos.br"
NODE_HOST="node006"
REMOTE_DIR="~/gtp5g/trisla"

# Verificar se está no diretório correto
if [ ! -f "README.md" ] || [ ! -d "apps" ]; then
    echo -e "${RED}❌ Erro: Execute este script no diretório raiz do projeto TriSLA${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Configuração:${NC}"
echo "   Origem: $(pwd)"
echo "   Destino: ${REMOTE_USER}@${NODE_HOST}:${REMOTE_DIR}"
echo "   Via: ${REMOTE_USER}@${PPGCA_HOST}"
echo ""

read -p "⚠️  Esta operação pode demorar. Deseja continuar? (s/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${YELLOW}❌ Operação cancelada${NC}"
    exit 0
fi

echo ""

# Método 1: Criar tar e copiar (mais eficiente)
echo -e "${YELLOW}📦 Criando arquivo tar...${NC}"
TAR_FILE="/tmp/trisla-$(date +%Y%m%d-%H%M%S).tar.gz"
tar -czf "$TAR_FILE" \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    --exclude='*.log' \
    --exclude='TriSLA_PROMPTS' \
    .

echo -e "${GREEN}✅ Arquivo tar criado: $TAR_FILE${NC}"
echo ""

# Etapa 1: Copiar para ppgca
echo -e "${YELLOW}📤 Etapa 1: Copiando para ${PPGCA_HOST}...${NC}"
scp "$TAR_FILE" "${REMOTE_USER}@${PPGCA_HOST}:/tmp/"
echo -e "${GREEN}✅ Arquivo copiado para ${PPGCA_HOST}${NC}"
echo ""

# Etapa 2: Copiar de ppgca para node006 e extrair
echo -e "${YELLOW}📤 Etapa 2: Copiando para ${NODE_HOST} e extraindo...${NC}"
ssh "${REMOTE_USER}@${PPGCA_HOST}" << EOF
    # Copiar para node006
    scp /tmp/$(basename $TAR_FILE) ${REMOTE_USER}@${NODE_HOST}:/tmp/
    
    # Conectar ao node006 e extrair
    ssh ${REMOTE_USER}@${NODE_HOST} << 'NODE_SCRIPT'
        # Criar diretório se não existir
        mkdir -p ${REMOTE_DIR}
        
        # Extrair arquivo
        cd ${REMOTE_DIR}
        tar -xzf /tmp/$(basename $TAR_FILE) --strip-components=0
        
        # Limpar arquivo temporário
        rm -f /tmp/$(basename $TAR_FILE)
        
        echo "✅ Projeto extraído em ${REMOTE_DIR}"
NODE_SCRIPT
    
    # Limpar arquivo temporário no ppgca
    rm -f /tmp/$(basename $TAR_FILE)
EOF

# Limpar arquivo local
rm -f "$TAR_FILE"

echo ""
echo -e "${GREEN}🎉 Projeto copiado com sucesso!${NC}"
echo ""
echo "📋 Próximos passos:"
echo "   1. Conectar ao NASP:"
echo "      ssh ${REMOTE_USER}@${PPGCA_HOST}"
echo "      ssh ${NODE_HOST}"
echo "   2. Ir para o diretório:"
echo "      cd ${REMOTE_DIR}"
echo "   3. Preparar deploy:"
echo "      bash scripts/prepare-nasp-deploy.sh"

