#!/bin/bash
# ============================================
# Pre-commit Hook: Validar Arquivos Públicos
# ============================================
# Previne commits de arquivos que não devem ser públicos
# ============================================

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
    "ansible/inventory.ini"
    "docs/ACESSO_NASP*.md"
    "docs/CONFIGURACAO_VALORES_REAIS.md"
    "docs/INFRAESTRUTURA_NASP.md"
)

# Verificar arquivos staged (apenas adicionados ou modificados, não deletados)
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACMR)

ERRORS=0

for file in $STAGED_FILES; do
    # Verificar se o arquivo existe (não está sendo deletado)
    if [ ! -f "$file" ]; then
        continue
    fi
    
    for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
        if [[ "$file" == $pattern ]] || [[ "$file" =~ ^$pattern ]]; then
            echo "❌ ERRO: Arquivo não público detectado: $file"
            echo "   Este arquivo não deve ser commitado no repositório público!"
            ERRORS=$((ERRORS + 1))
        fi
    done
    
    # Verificar se contém informações sensíveis (apenas para arquivos existentes)
    if [[ "$file" == *.md ]] || [[ "$file" == *.yaml ]] || [[ "$file" == *.yml ]]; then
        if git diff --cached "$file" 2>/dev/null | grep -qE "(192\.168\.|10\.|172\.|porvir5g|ppgca\.unisinos\.br|node006|node1|node2)"; then
            echo "⚠️  AVISO: Arquivo pode conter informações sensíveis: $file"
            echo "   Verifique se não há IPs, hosts ou credenciais reais"
        fi
    fi
done

if [ $ERRORS -gt 0 ]; then
    echo ""
    echo "🚫 Commit bloqueado! Remova os arquivos não públicos antes de commitar."
    echo ""
    echo "Para remover arquivos do staging:"
    echo "  git reset HEAD <arquivo>"
    echo ""
    exit 1
fi

exit 0


