#!/bin/bash
# ============================================
# Script: Remover FORÇADAMENTE TODOS os arquivos temporários
# ============================================
# Remove TODOS os arquivos que não devem ser públicos
# ============================================

set -e

echo "🧹 Removendo FORÇADAMENTE todos os arquivos temporários..."
echo ""

# Lista de padrões de arquivos a remover
PATTERNS=(
    "CORRECAO_*.md"
    "CORRECOES_*.md"
    "SOLUCAO_*.md"
    "RESUMO_*.md"
    "PROXIMOS_PASSOS_*.md"
    "PROXIMO_PASSO_*.md"
    "PROGRESSO_*.md"
    "LIMPEZA_*.md"
    "PLANO_LIMPEZA_*.md"
    "INSTRUCOES_LIMPEZA_*.md"
    "CORRECAO_FINAL_LIMPEZA.md"
    "LIMPEZA_FINAL_COMPLETA.md"
)

# Remover cada padrão
for pattern in "${PATTERNS[@]}"; do
    echo "Removendo: $pattern"
    # Tentar remover do Git (força mesmo se não existir)
    git rm -f $pattern 2>/dev/null || true
    # Remover arquivos específicos que podem existir
    for file in $pattern; do
        if [ -f "$file" ]; then
            git rm -f "$file" 2>/dev/null || true
        fi
    done
done

# Remover arquivos específicos conhecidos
echo ""
echo "Removendo arquivos específicos..."
SPECIFIC_FILES=(
    "CORRECAO_DOCKERFILE.md"
    "CORRECAO_SECURITY_SCAN.md"
    "CORRECAO_TAGS_IMAGENS.md"
    "CORRECAO_UI_DASHBOARD_BUILD.md"
    "CORRECAO_WORKFLOW_DEPLOY.md"
    "PROXIMO_PASSO_AGORA.md"
    "PROXIMO_PASSO_DEPLOY_NASP.md"
)

for file in "${SPECIFIC_FILES[@]}"; do
    if git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
        echo "  Removendo: $file"
        git rm -f "$file" 2>/dev/null || true
    fi
done

# Remover pasta TriSLA_PROMPTS se estiver rastreada
echo ""
echo "Verificando pasta TriSLA_PROMPTS..."
if git ls-files --error-unmatch TriSLA_PROMPTS/ >/dev/null 2>&1; then
    echo "⚠️  TriSLA_PROMPTS está sendo rastreado pelo Git!"
    echo "   Removendo do Git (arquivos locais serão mantidos)..."
    git rm -r --cached TriSLA_PROMPTS/ 2>/dev/null || true
fi

echo ""
echo "✅ Limpeza concluída!"
echo ""
echo "📋 Verifique os arquivos removidos:"
echo "   git status"
echo ""
echo "📝 Próximos passos:"
echo "   1. git add .gitignore .github/workflows/deploy.yml"
echo "   2. git commit -m 'chore: remover todos os arquivos temporários'"
echo "   3. git push origin main --force"


