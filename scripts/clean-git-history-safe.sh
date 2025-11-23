#!/bin/bash
# ============================================
# Script: Limpeza Segura do Histórico Git
# ============================================
# Remove arquivos privados do cache Git sem deletar localmente
# ============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Limpeza Segura do Histórico Git - TriSLA              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar se está em um repositório Git
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Erro: Não é um repositório Git${NC}"
    exit 1
fi

echo -e "${YELLOW}⚠️  ATENÇÃO: Este script irá remover arquivos privados do cache Git${NC}"
echo -e "${YELLOW}   Os arquivos serão mantidos localmente, mas não serão mais rastreados${NC}"
echo ""
read -p "Deseja continuar? (s/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Operação cancelada."
    exit 0
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}FASE 1: Removendo diretórios proibidos do cache Git${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

PROHIBITED_DIRS=(
    "TriSLA_PROMPTS"
    "private"
    "sandbox"
    "tmp"
    "venv"
    ".venv"
    "env"
)

for dir in "${PROHIBITED_DIRS[@]}"; do
    if git ls-files | grep -q "^$dir/"; then
        echo -e "${YELLOW}🗑️  Removendo $dir/ do cache Git...${NC}"
        git rm -r --cached "$dir/" 2>/dev/null || true
        echo -e "${GREEN}✅ $dir/ removido do cache${NC}"
    else
        echo -e "${GREEN}✅ $dir/ não está no cache Git${NC}"
    fi
done

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}FASE 2: Removendo arquivos de log do cache Git${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Remover arquivos .log
if git ls-files | grep -E '\.(log|out)$'; then
    echo -e "${YELLOW}🗑️  Removendo arquivos de log do cache Git...${NC}"
    git ls-files | grep -E '\.(log|out)$' | while read file; do
        git rm --cached "$file" 2>/dev/null || true
        echo -e "${GREEN}✅ Removido: $file${NC}"
    done
else
    echo -e "${GREEN}✅ Nenhum arquivo de log no cache Git${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}FASE 3: Removendo node_modules do cache Git${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if git ls-files | grep -q "^node_modules/"; then
    echo -e "${YELLOW}🗑️  Removendo node_modules/ do cache Git...${NC}"
    git rm -r --cached node_modules/ 2>/dev/null || true
    echo -e "${GREEN}✅ node_modules/ removido do cache${NC}"
else
    echo -e "${GREEN}✅ node_modules/ não está no cache Git${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}FASE 4: Removendo __pycache__ do cache Git${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if git ls-files | grep -q "__pycache__"; then
    echo -e "${YELLOW}🗑️  Removendo __pycache__ do cache Git...${NC}"
    git ls-files | grep "__pycache__" | while read file; do
        git rm --cached "$file" 2>/dev/null || true
    done
    echo -e "${GREEN}✅ __pycache__ removido do cache${NC}"
else
    echo -e "${GREEN}✅ __pycache__ não está no cache Git${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}FASE 5: Verificando arquivos sensíveis${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

SENSITIVE_PATTERNS=(
    "*.key"
    "*.pem"
    "*.token"
    "*.secret"
    "*.password"
    ".env.local"
    "gh_token"
    "github_token"
)

FOUND_SENSITIVE=false

for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if git ls-files | grep -q "$pattern"; then
        echo -e "${RED}⚠️  ATENÇÃO: Arquivo sensível encontrado: $pattern${NC}"
        FOUND_SENSITIVE=true
    fi
done

if [ "$FOUND_SENSITIVE" = true ]; then
    echo -e "${RED}❌ Arquivos sensíveis detectados!${NC}"
    echo -e "${YELLOW}   Revise manualmente antes de continuar${NC}"
    read -p "Deseja remover arquivos sensíveis do cache? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        for pattern in "${SENSITIVE_PATTERNS[@]}"; do
            git ls-files | grep "$pattern" | while read file; do
                git rm --cached "$file" 2>/dev/null || true
                echo -e "${GREEN}✅ Removido: $file${NC}"
            done
        done
    fi
else
    echo -e "${GREEN}✅ Nenhum arquivo sensível encontrado${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Resumo${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${GREEN}✅ Limpeza do cache Git concluída!${NC}"
echo ""
echo -e "${YELLOW}📋 Próximos passos:${NC}"
echo "   1. Revisar as mudanças: git status"
echo "   2. Adicionar .gitignore se ainda não estiver commitado: git add .gitignore"
echo "   3. Commit das mudanças: git commit -m 'chore: remove private files from git cache'"
echo "   4. Push: git push origin <branch>"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANTE:${NC}"
echo "   - Os arquivos ainda existem localmente"
echo "   - Eles não serão mais rastreados pelo Git"
echo "   - Certifique-se de que .gitignore está atualizado"
echo ""

