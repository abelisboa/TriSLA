#!/bin/bash
# ============================================
# Script para Preparar values-nasp.yaml
# ============================================
# Prepara o arquivo canônico values-nasp.yaml para deploy no NASP
# ============================================

set -e

# Verificar se está no diretório correto
if [ ! -f "README.md" ] || [ ! -d "helm" ] || [ ! -d "scripts" ]; then
    echo "❌ Erro: Execute este script no diretório raiz do projeto TriSLA"
    echo "   cd ~/gtp5g/trisla"
    exit 1
fi

VALUES_FILE="helm/trisla/values-nasp.yaml"

echo "🔧 Preparando values-nasp.yaml para deploy no NASP..."
echo ""

# Verificar se o arquivo existe
if [ ! -f "$VALUES_FILE" ]; then
    echo "❌ Arquivo não encontrado: $VALUES_FILE"
    echo "   O arquivo values-nasp.yaml deve existir em helm/trisla/"
    exit 1
fi

echo "✅ Arquivo canônico encontrado: $VALUES_FILE"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   1. Execute: ./scripts/discover-nasp-endpoints.sh"
echo "   2. Preencha os endpoints reais em $VALUES_FILE"
echo "   3. Valide: helm lint ./helm/trisla -f $VALUES_FILE"
echo "   4. Deploy: ./scripts/deploy-trisla-nasp-auto.sh"
echo ""

