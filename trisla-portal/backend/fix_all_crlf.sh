#!/bin/bash
# Script para corrigir CRLF → LF em TODOS os arquivos .sh e .py
# Garante formato UNIX puro

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "CORRIGIR CRLF → LF - TODOS OS ARQUIVOS"
echo "=========================================="
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

FIXED_COUNT=0

# Função para corrigir arquivo
fix_file() {
    local file="$1"
    if [ ! -f "$file" ]; then
        return 0
    fi
    
    # Verificar se tem CRLF
    if file "$file" | grep -q "CRLF\|CR line terminators"; then
        echo -e "${YELLOW}Corrigindo: $file${NC}"
        # Usar sed para remover CR
        sed -i 's/\r$//' "$file"
        ((FIXED_COUNT++))
        return 1
    else
        return 0
    fi
}

echo "Corrigindo arquivos .sh..."
for file in *.sh; do
    if [ -f "$file" ]; then
        fix_file "$file"
    fi
done

echo ""
echo "Corrigindo arquivos .sh em subdiretórios..."
for file in scripts/*.sh 2>/dev/null; do
    if [ -f "$file" ]; then
        fix_file "$file"
    fi
done

echo ""
echo "Corrigindo arquivos .py em src/..."
find src -name "*.py" -type f | while read -r file; do
    if file "$file" | grep -q "CRLF\|CR line terminators"; then
        echo -e "${YELLOW}Corrigindo: $file${NC}"
        sed -i 's/\r$//' "$file"
        ((FIXED_COUNT++))
    fi
done

echo ""
echo "=========================================="
if [ $FIXED_COUNT -gt 0 ]; then
    echo -e "${GREEN}✅ $FIXED_COUNT arquivo(s) corrigido(s)${NC}"
else
    echo -e "${GREEN}✅ Nenhum arquivo com CRLF encontrado${NC}"
fi
echo "=========================================="
echo ""
