#!/usr/bin/env bash
# Script para corrigir terminações de linha (CRLF → LF) em arquivos .sh
# Uso: ./scripts/fix-line-endings.sh
# Remove TODOS os caracteres \r (não apenas no final das linhas)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔧 [TriSLA] Corrigindo terminações de linha (CRLF → LF)..."

FIXED_COUNT=0

# Converter todos os scripts .sh
find "$REPO_ROOT" -type f -name "*.sh" | while read -r file; do
    if [ -f "$file" ]; then
        # Verificar se tem \r
        if grep -q $'\r' "$file" 2>/dev/null; then
            echo "   Corrigindo: $file"
            # Remover TODOS os \r (não apenas no final)
            sed -i 's/\r//g' "$file"
            ((FIXED_COUNT++))
        fi
    fi
done

# Garantir que scripts são executáveis
find "$REPO_ROOT" -type f -name "*.sh" -exec chmod +x {} \;

echo "✅ [TriSLA] Terminações de linha corrigidas!"
echo "📋 [TriSLA] Todos os scripts .sh agora usam LF (Unix)"

