#!/bin/bash
# Script para garantir formato UNIX puro (LF) em TODOS os arquivos
# Remove CRLF completamente

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "CORRIGIR CRLF → LF - TODOS OS ARQUIVOS"
echo "=========================================="
echo ""

FIXED_COUNT=0

# Função para corrigir arquivo
fix_file() {
    local file="$1"
    if [ ! -f "$file" ]; then
        return 0
    fi
    
    # Verificar e remover CRLF
    if grep -q $'\r' "$file" 2>/dev/null; then
        echo "   Corrigindo: $file"
        sed -i 's/\r$//' "$file"
        sed -i 's/\r//' "$file"
        ((FIXED_COUNT++))
        return 1
    fi
    return 0
}

echo "Corrigindo arquivos .sh na raiz..."
for file in *.sh; do
    if [ -f "$file" ]; then
        fix_file "$file"
    fi
done

echo ""
echo "Corrigindo arquivos .sh em scripts/..."
if [ -d "scripts" ]; then
    for file in scripts/*.sh; do
        if [ -f "$file" ]; then
            fix_file "$file"
        fi
    done
fi

echo ""
echo "Corrigindo arquivos .py em src/..."
find src -name "*.py" -type f | while read -r file; do
    if grep -q $'\r' "$file" 2>/dev/null; then
        echo "   Corrigindo: $file"
        sed -i 's/\r$//' "$file"
        sed -i 's/\r//' "$file"
        ((FIXED_COUNT++))
    fi
done

echo ""
echo "Corrigindo fix_crlf.py..."
if [ -f "fix_crlf.py" ]; then
    fix_file "fix_crlf.py"
fi

echo ""
echo "=========================================="
if [ $FIXED_COUNT -gt 0 ]; then
    echo "✅ $FIXED_COUNT arquivo(s) corrigido(s)"
else
    echo "✅ Nenhum arquivo com CRLF encontrado (já está em LF)"
fi
echo "=========================================="
echo ""

