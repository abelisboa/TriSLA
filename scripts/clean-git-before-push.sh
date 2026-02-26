#!/bin/bash
# ============================================
# Script: Clean Git Before Push
# ============================================
# Remove arquivos privados do índice Git antes do push
# ============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Clean Git Before Push - TriSLA                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar se está no diretório correto
if [ ! -f "README.md" ] || [ ! -d "helm" ] || [ ! -d "scripts" ]; then
    echo -e "${RED}❌ Erro: Execute este script no diretório raiz do projeto TriSLA${NC}"
    echo "   No node1 do NASP: cd ~/gtp5g/trisla"
    echo "   Localmente: cd /caminho/para/TriSLA-clean"
    exit 1
fi

# Verificar se é um repositório Git
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Erro: Não é um repositório Git${NC}"
    exit 1
fi

REMOVED_COUNT=0

echo -e "${YELLOW}🔍 Verificando arquivos privados no índice Git...${NC}"
echo ""

# Lista de diretórios/arquivos privados que NÃO devem estar no Git
PRIVATE_ITEMS=(
    "TriSLA_PROMPTS"
    "private"
    "sandbox"
    "tmp"
    "venv"
    ".venv"
    "*.log"
    "*.token"
    "*.secret"
    "*.pem"
    "*.key"
)

# Verificar cada item
for item in "${PRIVATE_ITEMS[@]}"; do
    # Verificar se está sendo rastreado pelo Git
    if git ls-files | grep -q "^$item" || git ls-files | grep -q "/$item"; then
        echo -e "${YELLOW}⚠️  Removendo $item do índice Git...${NC}"
        
        # Remover do índice (mantém localmente)
        if git rm -r --cached "$item" 2>/dev/null; then
            echo -e "${GREEN}✅ $item removido do índice Git${NC}"
            REMOVED_COUNT=$((REMOVED_COUNT + 1))
        else
            echo -e "${YELLOW}⏭️  $item não encontrado no índice Git${NC}"
        fi
    fi
done

# Verificar especificamente TriSLA_PROMPTS
if git ls-files | grep -q "TriSLA_PROMPTS"; then
    echo -e "${YELLOW}⚠️  Removendo TriSLA_PROMPTS/ do índice Git...${NC}"
    git rm -r --cached TriSLA_PROMPTS/ 2>/dev/null && {
        echo -e "${GREEN}✅ TriSLA_PROMPTS/ removido do índice Git${NC}"
        REMOVED_COUNT=$((REMOVED_COUNT + 1))
    } || echo -e "${YELLOW}⏭️  TriSLA_PROMPTS/ não encontrado no índice Git${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Relatório Final${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ $REMOVED_COUNT -gt 0 ]; then
    echo -e "${GREEN}✅ $REMOVED_COUNT item(s) removido(s) do índice Git${NC}"
    echo ""
    echo -e "${YELLOW}📋 Próximos passos:${NC}"
    echo "   1. Verificar mudanças: git status"
    echo "   2. Commit da remoção: git commit -m 'chore: remove private files from Git index'"
    echo "   3. Push para GitHub: git push origin main"
else
    echo -e "${GREEN}✅ Nenhum arquivo privado encontrado no índice Git${NC}"
fi

echo ""
echo -e "${YELLOW}⚠️  IMPORTANTE:${NC}"
echo "   - Arquivos foram removidos do índice Git, mas ainda existem localmente"
echo "   - Eles não serão mais rastreados pelo Git"
echo "   - Certifique-se de que estão no .gitignore"

echo ""

