#!/bin/bash
# ============================================
# Script de Validação Helm
# ============================================

set -e

CHART_PATH="./helm/trisla"

echo "🔍 Validando Helm Chart..."

# 1. Lint
echo "1️⃣ Executando helm lint..."
helm lint "$CHART_PATH"

# Verificar se está no diretório correto
if [ ! -f "README.md" ] || [ ! -d "helm" ] || [ ! -d "scripts" ]; then
    echo "❌ Erro: Execute este script no diretório raiz do projeto TriSLA"
    echo "   cd ~/gtp5g/trisla"
    exit 1
fi

# 2. Template
echo "2️⃣ Gerando templates..."
helm template trisla "$CHART_PATH" -f "$CHART_PATH/values-nasp.yaml" --debug > /tmp/trisla-templates.yaml
echo "✅ Templates gerados em /tmp/trisla-templates.yaml"

# 3. Validação de sintaxe
echo "3️⃣ Validando sintaxe YAML..."
kubectl apply --dry-run=client -f /tmp/trisla-templates.yaml

# 4. Verificar valores obrigatórios
echo "4️⃣ Verificando valores obrigatórios..."
if [ -z "$TRISLA_NODE_IP" ]; then
    echo "⚠️  TRISLA_NODE_IP não configurado"
fi

echo "✅ Validação Helm concluída!"

