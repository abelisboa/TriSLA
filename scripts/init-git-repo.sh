#!/bin/bash
# ============================================
# Script para Inicializar Repositório Git
# ============================================
# Inicializa Git e configura conexão com GitHub
# ============================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

GITHUB_REPO="abelisboa/TriSLA"
GITHUB_URL="https://github.com/${GITHUB_REPO}.git"

echo -e "${GREEN}🔧 Inicializando repositório Git...${NC}"
echo ""

# Verificar se já é um repositório Git
if [ -d ".git" ]; then
    echo -e "${YELLOW}⚠️  Já é um repositório Git${NC}"
    read -p "Deseja reconfigurar? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 0
    fi
fi

# 1. Inicializar Git
echo -e "${YELLOW}📁 Inicializando Git...${NC}"
git init
echo -e "${GREEN}✅ Git inicializado${NC}"
echo ""

# 2. Configurar remote
echo -e "${YELLOW}🔗 Configurando remote GitHub...${NC}"
git remote remove origin 2>/dev/null || true
git remote add origin "$GITHUB_URL"
echo -e "${GREEN}✅ Remote configurado: $GITHUB_URL${NC}"
echo ""

# 3. Verificar se o repositório remoto existe
echo -e "${YELLOW}🔍 Verificando repositório remoto...${NC}"
if git ls-remote --heads origin main &>/dev/null; then
    echo -e "${GREEN}✅ Repositório remoto encontrado${NC}"
    echo -e "${YELLOW}⚠️  O repositório remoto já existe. Você pode:${NC}"
    echo "   1. Fazer pull primeiro: git pull origin main --allow-unrelated-histories"
    echo "   2. Ou fazer force push: git push -f origin main (CUIDADO: apaga tudo no remoto)"
    echo ""
    read -p "Deseja fazer pull primeiro? (S/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo -e "${YELLOW}📥 Fazendo pull...${NC}"
        git pull origin main --allow-unrelated-histories || {
            echo -e "${YELLOW}⚠️  Pull falhou. Continuando sem pull...${NC}"
        }
    fi
else
    echo -e "${YELLOW}⚠️  Repositório remoto não encontrado ou está vazio${NC}"
    echo "   Certifique-se de que o repositório existe em: https://github.com/$GITHUB_REPO"
fi
echo ""

# 4. Configurar branch main
echo -e "${YELLOW}🌿 Configurando branch main...${NC}"
git branch -M main
echo -e "${GREEN}✅ Branch main configurada${NC}"
echo ""

# 5. Status
echo -e "${YELLOW}📊 Status do repositório:${NC}"
git status
echo ""

echo -e "${GREEN}✅ Repositório Git configurado!${NC}"
echo ""
echo "📋 Próximos passos:"
echo "   1. Revisar arquivos: git status"
echo "   2. Adicionar arquivos: git add ."
echo "   3. Fazer commit: git commit -m '🚀 TriSLA: Arquitetura completa para garantia de SLA em redes 5G/O-RAN'"
echo "   4. Fazer push: git push -u origin main"
echo ""
echo "⚠️  ATENÇÃO: O .gitignore já está configurado para excluir:"
echo "   - TriSLA_PROMPTS/"
echo "   - Arquivos com tokens/secrets"
echo "   - Configurações locais do NASP"

