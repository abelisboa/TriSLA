#!/usr/bin/env bash
# Script robusto para corrigir terminações de linha (CRLF → LF) em TODOS os arquivos
# Remove TODOS os caracteres \r (não apenas no final das linhas)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔧 [TriSLA] Corrigindo terminações de linha (CRLF → LF) em TODOS os arquivos..."
echo ""

FIXED_COUNT=0

# Função para corrigir arquivo
fix_file() {
    local file="$1"
    if [ ! -f "$file" ]; then
        return 0
    fi
    
    # Verificar se tem \r
    if grep -q $'\r' "$file" 2>/dev/null; then
        echo "   Corrigindo: $file"
        # Remover TODOS os \r (não apenas no final)
        sed -i 's/\r//g' "$file"
        ((FIXED_COUNT++))
        return 1
    fi
    return 0
}

# Corrigir todos os scripts .sh
echo "📋 Corrigindo arquivos .sh..."
find "$REPO_ROOT" -type f -name "*.sh" | while read -r file; do
    fix_file "$file"
done

# Corrigir arquivos Python também (podem ter CRLF)
echo "📋 Corrigindo arquivos .py..."
find "$REPO_ROOT" -type f -name "*.py" | while read -r file; do
    if grep -q $'\r' "$file" 2>/dev/null; then
        echo "   Corrigindo: $file"
        sed -i 's/\r//g' "$file"
        ((FIXED_COUNT++))
    fi
done

# Garantir que scripts são executáveis
echo "📋 Tornando scripts executáveis..."
find "$REPO_ROOT" -type f -name "*.sh" -exec chmod +x {} \;

echo ""
echo "✅ [TriSLA] Correção concluída!"
echo "📋 [TriSLA] Todos os arquivos .sh e .py agora usam LF (Unix)"
echo ""
echo "Teste os scripts:"
echo "  cd besu && ./scripts/start_besu.sh"
echo "  cd besu && ./scripts/check_besu.sh"

