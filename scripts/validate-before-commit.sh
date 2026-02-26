#!/bin/bash
# ============================================
# Script: Validar Antes de Commit
# ============================================
# Valida se há arquivos não públicos no staging
# ============================================

set -e

echo "🔍 Validando arquivos antes do commit..."
echo ""

# Padrões de arquivos que NÃO devem ser commitados
FORBIDDEN_PATTERNS=(
    "TriSLA_PROMPTS/"
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
    "COMANDO_*.md"
    "COMANDOS_*.md"
    "GUIA_*.md"
    "CORRIGIR_*.md"
    "ACAO_*.md"
    "VERIFICAR_*.md"
    "REMOVER_*.md"
    "*.zip"
)

# Verificar arquivos staged
STAGED_FILES=$(git diff --cached --name-only 2>/dev/null || echo "")

if [ -z "$STAGED_FILES" ]; then
    echo "⚠️  Nenhum arquivo no staging. Execute 'git add' primeiro."
    exit 0
fi

ERRORS=0
WARNINGS=0

echo "📋 Arquivos no staging:"
echo "$STAGED_FILES" | while read -r file; do
    echo "  - $file"
    
    # Verificar padrões proibidos
    for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
        if [[ "$file" == $pattern ]] || [[ "$file" =~ ^$pattern ]]; then
            echo "    ❌ ERRO: Arquivo não público detectado!"
            ERRORS=$((ERRORS + 1))
        fi
    done
    
    # Verificar informações sensíveis
    if [[ "$file" == *.md ]] || [[ "$file" == *.yaml ]] || [[ "$file" == *.yml ]] || [[ "$file" == *.ini ]]; then
        if git diff --cached "$file" 2>/dev/null | grep -qE "(192\.168\.|10\.|172\.|porvir5g|ppgca\.unisinos\.br|node006|ghp_|gho_)"; then
            echo "    ⚠️  AVISO: Possível informação sensível detectada!"
            WARNINGS=$((WARNINGS + 1))
        fi
    fi
done

echo ""
if [ $ERRORS -gt 0 ]; then
    echo "❌ ERRO: $ERRORS arquivo(s) não público(s) detectado(s)!"
    echo "   Remova esses arquivos do staging antes de commitar."
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo "⚠️  AVISO: $WARNINGS possível(is) informação(ões) sensível(is) detectada(s)."
    echo "   Verifique se não há dados reais antes de commitar."
    exit 0
else
    echo "✅ Nenhum problema detectado. Pronto para commit!"
    exit 0
fi


