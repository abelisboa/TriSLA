#!/usr/bin/env bash
# Script para corrigir CRLF em TODOS os scripts do BESU

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BESU_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔧 [TriSLA] Corrigindo CRLF em todos os scripts do BESU..."
echo ""

FIXED=0

# Corrigir todos os scripts .sh
find "$BESU_DIR" -type f -name "*.sh" | while read -r file; do
    if grep -q $'\r' "$file" 2>/dev/null; then
        echo "   Corrigindo: $file"
        # Remover TODOS os \r (não apenas no final)
        sed -i 's/\r//g' "$file"
        ((FIXED++))
    fi
done

# Garantir que scripts são executáveis
find "$BESU_DIR" -type f -name "*.sh" -exec chmod +x {} \;

echo ""
echo "✅ [TriSLA] Correção concluída!"
echo "📋 [TriSLA] Todos os scripts .sh agora usam LF (Unix)"
echo ""
echo "Teste os scripts:"
echo "  cd besu/scripts"
echo "  bash wait-and-test-besu.sh"

