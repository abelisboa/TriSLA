#!/bin/bash
# ============================================
# Script para Preencher values-production.yaml
# ============================================
# Preenche valores reais do NASP no arquivo values-production.yaml
# ============================================

set -e

VALUES_FILE="helm/trisla/values-nasp.yaml"
VALUES_PROD_FILE="helm/trisla/values-production.yaml"

echo "🔧 Preenchendo valores de produção..."
echo ""

# Verificar se o arquivo existe
if [ ! -f "$VALUES_FILE" ]; then
    echo "❌ Arquivo não encontrado: $VALUES_FILE"
    echo "   Execute este script no diretório raiz do projeto TriSLA"
    exit 1
fi

# Copiar values-nasp.yaml para values-production.yaml
echo "📋 Copiando $VALUES_FILE para $VALUES_PROD_FILE..."
cp "$VALUES_FILE" "$VALUES_PROD_FILE"

echo "✅ Arquivo $VALUES_PROD_FILE atualizado"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   1. Execute: ./scripts/discover-nasp-endpoints.sh"
echo "   2. Preencha os endpoints reais em $VALUES_PROD_FILE"
echo "   3. Valide: helm lint ./helm/trisla -f $VALUES_PROD_FILE"
echo ""

