#!/bin/bash
# ============================================
# Script para Verificar se TriSLA está no NASP
# ============================================
# Verifica se o projeto já está clonado/copiado no NASP
# ============================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔍 Verificando se TriSLA está no NASP...${NC}"
echo ""

# Verificar se está no NASP
if ! kubectl cluster-info &>/dev/null; then
    echo -e "${RED}❌ Erro: Não está conectado ao cluster Kubernetes${NC}"
    echo "Execute este script no NASP (node1)"
    exit 1
fi

REMOTE_DIR="$HOME/gtp5g/trisla"
REMOTE_DIR_ALT="$HOME/trisla"

echo -e "${YELLOW}📋 Verificando diretórios:${NC}"
echo "   - $REMOTE_DIR"
echo "   - $REMOTE_DIR_ALT"
echo ""

# Verificar se o diretório existe
FOUND=false
CHECK_DIR=""

if [ -d "$REMOTE_DIR" ]; then
    CHECK_DIR="$REMOTE_DIR"
    FOUND=true
    echo -e "${GREEN}✅ Diretório encontrado: $REMOTE_DIR${NC}"
elif [ -d "$REMOTE_DIR_ALT" ]; then
    CHECK_DIR="$REMOTE_DIR_ALT"
    FOUND=true
    echo -e "${GREEN}✅ Diretório encontrado: $REMOTE_DIR_ALT${NC}"
else
    echo -e "${RED}❌ Diretório não encontrado${NC}"
    echo ""
    echo "📋 Próximos passos:"
    echo "   1. Clonar do GitHub:"
    echo "      cd ~/gtp5g"
    echo "      git clone https://github.com/abelisboa/TriSLA.git trisla"
    echo "   2. O projeto deve estar em: ~/gtp5g/trisla"
    echo "      (Scripts de cópia foram descontinuados - deploy é local)"
    exit 1
fi

echo ""

# Verificar conteúdo do diretório
if [ -f "$CHECK_DIR/README.md" ] && [ -d "$CHECK_DIR/apps" ] && [ -d "$CHECK_DIR/helm" ]; then
    echo -e "${GREEN}✅ Estrutura do projeto encontrada${NC}"
    echo ""
    
    # Verificar se é um repositório Git
    if [ -d "$CHECK_DIR/.git" ]; then
        echo -e "${GREEN}✅ É um repositório Git${NC}"
        echo ""
        echo -e "${YELLOW}📋 Informações do repositório:${NC}"
        cd "$CHECK_DIR"
        echo "   Remote: $(git remote get-url origin 2>/dev/null || echo 'N/A')"
        echo "   Branch: $(git branch --show-current 2>/dev/null || echo 'N/A')"
        echo "   Último commit: $(git log -1 --oneline 2>/dev/null || echo 'N/A')"
        echo ""
        
        # Verificar se está atualizado
        echo -e "${YELLOW}🔄 Verificando atualizações...${NC}"
        git fetch origin 2>/dev/null || echo "   ⚠️  Não foi possível verificar atualizações"
        LOCAL=$(git rev-parse @ 2>/dev/null || echo "")
        REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "")
        
        if [ -n "$LOCAL" ] && [ -n "$REMOTE" ]; then
            if [ "$LOCAL" = "$REMOTE" ]; then
                echo -e "${GREEN}✅ Repositório está atualizado${NC}"
            else
                echo -e "${YELLOW}⚠️  Repositório precisa ser atualizado${NC}"
                echo "   Execute: cd $CHECK_DIR && git pull origin main"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  Não é um repositório Git (foi copiado manualmente)${NC}"
        echo ""
        echo "💡 Recomendação: Clonar do GitHub para facilitar atualizações"
        echo "   cd ~/gtp5g"
        echo "   rm -rf trisla"
        echo "   git clone https://github.com/abelisboa/TriSLA.git trisla"
    fi
    
    echo ""
    echo -e "${YELLOW}📁 Estrutura encontrada:${NC}"
    echo "   - README.md: $([ -f "$CHECK_DIR/README.md" ] && echo '✅' || echo '❌')"
    echo "   - apps/: $([ -d "$CHECK_DIR/apps" ] && echo '✅' || echo '❌')"
    echo "   - helm/: $([ -d "$CHECK_DIR/helm" ] && echo '✅' || echo '❌')"
    echo "   - scripts/: $([ -d "$CHECK_DIR/scripts" ] && echo '✅' || echo '❌')"
    echo "   - ansible/: $([ -d "$CHECK_DIR/ansible" ] && echo '✅' || echo '❌')"
    echo ""
    
    echo -e "${GREEN}🎉 Projeto TriSLA encontrado!${NC}"
    echo ""
    echo "📋 Próximos passos:"
    echo "   1. Ir para o diretório:"
    echo "      cd $CHECK_DIR"
    echo "   2. Preparar deploy:"
    echo "      bash scripts/prepare-nasp-deploy.sh"
    echo "   3. Fazer deploy:"
    echo "      bash scripts/deploy-trisla-nasp.sh"
    
else
    echo -e "${RED}❌ Estrutura do projeto incompleta${NC}"
    echo ""
    echo "📋 Arquivos/diretórios esperados:"
    echo "   - README.md: $([ -f "$CHECK_DIR/README.md" ] && echo '✅' || echo '❌')"
    echo "   - apps/: $([ -d "$CHECK_DIR/apps" ] && echo '✅' || echo '❌')"
    echo "   - helm/: $([ -d "$CHECK_DIR/helm" ] && echo '✅' || echo '❌')"
    echo ""
    echo "💡 Recomendação: Clonar do GitHub novamente"
    echo "   cd ~/gtp5g"
    echo "   rm -rf trisla"
    echo "   git clone https://github.com/abelisboa/TriSLA.git trisla"
fi

