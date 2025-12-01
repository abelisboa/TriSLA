#!/bin/bash
# ============================================
# Script: Instalar Pre-commit Hook
# ============================================
# Copia o hook de validação para .git/hooks/
# ============================================

set -e

HOOK_SOURCE="scripts/pre-commit-hook.sh"
HOOK_TARGET=".git/hooks/pre-commit"

if [ ! -f "$HOOK_SOURCE" ]; then
    echo "❌ Erro: $HOOK_SOURCE não encontrado"
    exit 1
fi

echo "📋 Instalando pre-commit hook..."
cp "$HOOK_SOURCE" "$HOOK_TARGET"
chmod +x "$HOOK_TARGET"

echo "✅ Pre-commit hook instalado com sucesso!"
echo ""
echo "O hook validará automaticamente antes de cada commit."


