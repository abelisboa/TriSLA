#!/bin/bash
# ============================================
# Script: Remover Arquivos Específicos do Git
# ============================================
# Remove arquivos específicos que ainda estão no Git
# ============================================

set -e

echo "🧹 Removendo arquivos específicos do Git..."
echo ""

# Arquivos específicos que ainda estão no GitHub
SPECIFIC_FILES=(
    "CORRECAO_DOCKERFILE.md"
    "CORRECAO_TAGS_IMAGENS.md"
    "PROXIMO_PASSO_AGORA.md"
)

# Verificar e remover cada arquivo
for file in "${SPECIFIC_FILES[@]}"; do
    if git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
        echo "  ✅ Removendo: $file"
        git rm -f "$file" 2>/dev/null || true
    else
        echo "  ⚠️  $file não está rastreado pelo Git (pode já ter sido removido)"
    fi
done

# Tentar remover por padrões também
echo ""
echo "Removendo por padrões..."
git rm -f CORRECAO_*.md PROXIMO_PASSO_*.md 2>/dev/null || true

echo ""
echo "✅ Verificando status..."
git status --short | head -20

echo ""
echo "📋 Se os arquivos ainda aparecerem, execute:"
echo "   git rm --cached <arquivo>"
echo "   git commit --amend"
echo "   git push origin main --force"


