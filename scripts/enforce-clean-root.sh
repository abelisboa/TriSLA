#!/bin/bash
# ============================================
# Script: Enforce Clean Root
# ============================================
# Garante que apenas arquivos e pastas permitidos estejam na raiz
# ============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Enforce Clean Root - TriSLA                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar se está no diretório correto
if [ ! -f "README.md" ] || [ ! -d "helm" ] || [ ! -d "scripts" ]; then
    echo -e "${RED}❌ Erro: Execute este script no diretório raiz do projeto TriSLA${NC}"
    echo "   cd ~/gtp5g/trisla"
    exit 1
fi

# Arquivos permitidos na raiz
ALLOWED_FILES=("README.md" "LICENSE" ".gitignore" "CHANGELOG.md")

# Pastas permitidas na raiz
ALLOWED_DIRS=("helm" "ansible" "scripts" "docs" "monitoring" "tests" "apps" "configs" "nasp" "tools" ".github")

# Listar itens na raiz
echo -e "${YELLOW}🔍 Escaneando raiz do repositório...${NC}"
echo ""

ROOT_ITEMS=$(find . -maxdepth 1 -not -path '*/\.*' -not -path '.' | sed 's|^\./||' | sort)

PROHIBITED_FILES=()
PROHIBITED_DIRS=()

# Verificar cada item
while IFS= read -r item; do
    if [ -z "$item" ]; then
        continue
    fi
    
    if [ -f "$item" ]; then
        # É um arquivo
        ALLOWED=false
        for allowed in "${ALLOWED_FILES[@]}"; do
            if [[ "$item" == "$allowed" ]]; then
                ALLOWED=true
                break
            fi
        done
        
        if [ "$ALLOWED" = false ]; then
            PROHIBITED_FILES+=("$item")
        fi
    elif [ -d "$item" ]; then
        # É um diretório
        ALLOWED=false
        for allowed in "${ALLOWED_DIRS[@]}"; do
            if [[ "$item" == "$allowed" ]]; then
                ALLOWED=true
                break
            fi
        done
        
        if [ "$ALLOWED" = false ]; then
            PROHIBITED_DIRS+=("$item")
        fi
    fi
done <<< "$ROOT_ITEMS"

# Verificações específicas
MD_FILES=$(find . -maxdepth 1 -name "*.md" -not -name "README.md" -not -name "CHANGELOG.md" 2>/dev/null | sed 's|^\./||' || true)
SH_FILES=$(find . -maxdepth 1 -name "*.sh" 2>/dev/null | sed 's|^\./||' || true)
YAML_FILES=$(find . -maxdepth 1 \( -name "*.yaml" -o -name "*.yml" \) 2>/dev/null | sed 's|^\./||' || true)
SOLO_FILES=$(find . -maxdepth 1 \( -name "*.txt" -o -name "*.log" -o -name "*.json" -o -name "*.pdf" -o -name "*.png" -o -name "*.jpg" \) 2>/dev/null | sed 's|^\./||' || true)
PRIVATE_DIRS=$(find . -maxdepth 1 -type d \( -name "TriSLA_PROMPTS" -o -name "private" -o -name "sandbox" -o -name "tmp" -o -name "venv" -o -name ".venv" \) 2>/dev/null | sed 's|^\./||' || true)

# Consolidar itens proibidos
if [ -n "$MD_FILES" ]; then
    while IFS= read -r file; do
        if [ -n "$file" ]; then
            PROHIBITED_FILES+=("$file")
        fi
    done <<< "$MD_FILES"
fi

if [ -n "$SH_FILES" ]; then
    while IFS= read -r file; do
        if [ -n "$file" ]; then
            PROHIBITED_FILES+=("$file")
        fi
    done <<< "$SH_FILES"
fi

if [ -n "$YAML_FILES" ]; then
    while IFS= read -r file; do
        if [ -n "$file" ]; then
            PROHIBITED_FILES+=("$file")
        fi
    done <<< "$YAML_FILES"
fi

if [ -n "$SOLO_FILES" ]; then
    while IFS= read -r file; do
        if [ -n "$file" ]; then
            PROHIBITED_FILES+=("$file")
        fi
    done <<< "$SOLO_FILES"
fi

if [ -n "$PRIVATE_DIRS" ]; then
    while IFS= read -r dir; do
        if [ -n "$dir" ]; then
            PROHIBITED_DIRS+=("$dir")
        fi
    done <<< "$PRIVATE_DIRS"
fi

# Remover duplicatas
PROHIBITED_FILES=($(printf '%s\n' "${PROHIBITED_FILES[@]}" | sort -u))
PROHIBITED_DIRS=($(printf '%s\n' "${PROHIBITED_DIRS[@]}" | sort -u))

# Exibir resultados
TOTAL_PROHIBITED=$((${#PROHIBITED_FILES[@]} + ${#PROHIBITED_DIRS[@]}))

if [ $TOTAL_PROHIBITED -eq 0 ]; then
    echo -e "${GREEN}✅ Raiz do repositório está limpa!${NC}"
    echo ""
    echo -e "${GREEN}📋 Estrutura válida:${NC}"
    echo "   Arquivos permitidos: ${ALLOWED_FILES[*]}"
    echo "   Diretórios permitidos: ${ALLOWED_DIRS[*]}"
    exit 0
fi

echo -e "${YELLOW}⚠️  Itens proibidos encontrados na raiz:${NC}"
echo ""

if [ ${#PROHIBITED_FILES[@]} -gt 0 ]; then
    echo -e "${RED}📄 Arquivos proibidos:${NC}"
    for file in "${PROHIBITED_FILES[@]}"; do
        echo "   - $file"
    done
    echo ""
fi

if [ ${#PROHIBITED_DIRS[@]} -gt 0 ]; then
    echo -e "${RED}📁 Diretórios proibidos:${NC}"
    for dir in "${PROHIBITED_DIRS[@]}"; do
        echo "   - $dir"
    done
    echo ""
fi

echo -e "${YELLOW}📋 Ações disponíveis:${NC}"
echo ""
echo "   (a) Mover automaticamente para pasta correta"
echo "   (b) Remover do índice Git (mantém localmente)"
echo "   (c) Abortar e revisar manualmente"
echo ""
read -p "Escolha uma ação (a/b/c): " -n 1 -r
echo ""

case $REPLY in
    [Aa]*)
        echo ""
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BLUE}Movendo arquivos para pastas corretas...${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        
        # Criar docs/reports se não existir
        mkdir -p docs/reports
        
        MOVED_COUNT=0
        
        # Mover arquivos .md para docs/reports/
        for file in "${PROHIBITED_FILES[@]}"; do
            if [[ "$file" == *.md ]]; then
                echo -e "${YELLOW}📦 Movendo $file → docs/reports/${NC}"
                mv "$file" "docs/reports/" 2>/dev/null || true
                MOVED_COUNT=$((MOVED_COUNT + 1))
            elif [[ "$file" == *.sh ]]; then
                echo -e "${YELLOW}📦 Movendo $file → scripts/${NC}"
                mv "$file" "scripts/" 2>/dev/null || true
                MOVED_COUNT=$((MOVED_COUNT + 1))
            elif [[ "$file" == *.yaml ]] || [[ "$file" == *.yml ]]; then
                echo -e "${YELLOW}📦 Movendo $file → configs/${NC}"
                mkdir -p configs
                mv "$file" "configs/" 2>/dev/null || true
                MOVED_COUNT=$((MOVED_COUNT + 1))
            else
                echo -e "${YELLOW}📦 Movendo $file → docs/reports/${NC}"
                mv "$file" "docs/reports/" 2>/dev/null || true
                MOVED_COUNT=$((MOVED_COUNT + 1))
            fi
        done
        
        echo ""
        echo -e "${GREEN}✅ $MOVED_COUNT arquivo(s) movido(s)${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  Diretórios proibidos devem ser removidos manualmente ou adicionados ao .gitignore${NC}"
        ;;
        
    [Bb]*)
        echo ""
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BLUE}Removendo do índice Git...${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        
        REMOVED_COUNT=0
        
        # Remover arquivos do índice Git
        for file in "${PROHIBITED_FILES[@]}"; do
            if git ls-files --error-unmatch "$file" &>/dev/null; then
                echo -e "${YELLOW}🗑️  Removendo $file do índice Git${NC}"
                git rm --cached "$file" 2>/dev/null || true
                REMOVED_COUNT=$((REMOVED_COUNT + 1))
            fi
        done
        
        # Remover diretórios do índice Git
        for dir in "${PROHIBITED_DIRS[@]}"; do
            if git ls-files --error-unmatch "$dir" &>/dev/null 2>&1; then
                echo -e "${YELLOW}🗑️  Removendo $dir/ do índice Git${NC}"
                git rm -r --cached "$dir/" 2>/dev/null || true
                REMOVED_COUNT=$((REMOVED_COUNT + 1))
            fi
        done
        
        echo ""
        echo -e "${GREEN}✅ $REMOVED_COUNT item(s) removido(s) do índice Git${NC}"
        echo -e "${YELLOW}⚠️  Arquivos ainda existem localmente. Revise antes de commitar.${NC}"
        ;;
        
    [Cc]*)
        echo ""
        echo -e "${YELLOW}⏸️  Operação abortada. Revise manualmente os itens proibidos.${NC}"
        echo ""
        echo -e "${YELLOW}📋 Próximos passos:${NC}"
        echo "   1. Mover ou remover itens proibidos manualmente"
        echo "   2. Executar este script novamente para validar"
        exit 0
        ;;
        
    *)
        echo -e "${RED}❌ Opção inválida. Operação abortada.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Relatório Final${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Verificar novamente
ROOT_ITEMS_AFTER=$(find . -maxdepth 1 -not -path '*/\.*' -not -path '.' | sed 's|^\./||' | sort)
PROHIBITED_AFTER=0

while IFS= read -r item; do
    if [ -z "$item" ]; then
        continue
    fi
    
    if [ -f "$item" ]; then
        ALLOWED=false
        for allowed in "${ALLOWED_FILES[@]}"; do
            if [[ "$item" == "$allowed" ]]; then
                ALLOWED=true
                break
            fi
        done
        if [ "$ALLOWED" = false ]; then
            PROHIBITED_AFTER=$((PROHIBITED_AFTER + 1))
        fi
    elif [ -d "$item" ]; then
        ALLOWED=false
        for allowed in "${ALLOWED_DIRS[@]}"; do
            if [[ "$item" == "$allowed" ]]; then
                ALLOWED=true
                break
            fi
        done
        if [ "$ALLOWED" = false ]; then
            PROHIBITED_AFTER=$((PROHIBITED_AFTER + 1))
        fi
    fi
done <<< "$ROOT_ITEMS_AFTER"

if [ $PROHIBITED_AFTER -eq 0 ]; then
    echo -e "${GREEN}✅ Raiz do repositório está limpa!${NC}"
    echo ""
    echo -e "${GREEN}📋 Estrutura final:${NC}"
    echo "   Arquivos permitidos: ${ALLOWED_FILES[*]}"
    echo "   Diretórios permitidos: ${ALLOWED_DIRS[*]}"
else
    echo -e "${YELLOW}⚠️  Ainda há $PROHIBITED_AFTER item(s) proibido(s) na raiz${NC}"
    echo "   Execute este script novamente ou revise manualmente"
fi

echo ""

