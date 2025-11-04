#!/bin/bash
# Script completo para executar no node1
# Execute na pasta: ~/gtp5g/trisla-portal

set -e

echo "=========================================="
echo "🚀 Setup Dashboard Customizado TriSLA"
echo "=========================================="
echo ""

# Verificar se está na pasta correta
if [ ! -d "apps/api" ]; then
    echo "❌ Execute este script da pasta ~/gtp5g/trisla-portal"
    exit 1
fi

# Criar diretórios
mkdir -p apps/api
mkdir -p apps/ui/src/pages

echo "✅ Diretórios criados"
echo ""

# Criar prometheus.py (arquivo completo)
echo "📝 Criando: apps/api/prometheus.py"
# [O conteúdo completo será adicionado via cat heredoc]
# Por limitação de tamanho, vou criar um script separado ou comandos individuais

echo ""
echo "✅ Execute os comandos individuais abaixo para criar cada arquivo:"
echo ""





