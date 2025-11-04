#!/bin/bash
# Script para criar dashboards diretamente no node1
# Execute este script no node1

set -e

echo "=========================================="
echo "📊 Criando Dashboards no node1"
echo "=========================================="
echo ""

DASHBOARDS_DIR="$HOME/gtp5g/trisla-portal/grafana-dashboards"

# Criar diretório
mkdir -p "$DASHBOARDS_DIR"
cd "$HOME/gtp5g/trisla-portal"

echo "📁 Diretório criado: $DASHBOARDS_DIR"
echo ""

# Verificar se já existem arquivos
if ls "$DASHBOARDS_DIR"/*.json 1> /dev/null 2>&1; then
    echo "⚠️  Já existem arquivos JSON no diretório:"
    ls -lh "$DASHBOARDS_DIR"/*.json
    echo ""
    read -p "Deseja sobrescrever? (s/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "❌ Operação cancelada"
        exit 1
    fi
fi

echo "📝 Os arquivos JSON dos dashboards precisam ser criados."
echo "   Opções:"
echo ""
echo "   1. Copiar do repositório Git (se estiver disponível)"
echo "   2. Criar manualmente via interface web do Grafana"
echo "   3. Baixar de URL se os arquivos estiverem em um repositório"
echo ""
echo "🔍 Verificando se existe repositório Git..."
echo ""

# Verificar se é repositório git
if [ -d ".git" ]; then
    echo "✅ Diretório é um repositório Git"
    echo "   Tentando atualizar via git pull..."
    
    if git pull origin main 2>/dev/null || git pull origin master 2>/dev/null; then
        if [ -d "grafana-dashboards" ] && [ "$(ls -A grafana-dashboards/*.json 2>/dev/null)" ]; then
            echo "✅ Dashboards encontrados no repositório!"
            ls -lh grafana-dashboards/*.json
            exit 0
        fi
    fi
    echo "⚠️  Git pull executado, mas dashboards não encontrados no repo"
fi

echo ""
echo "📋 Próximos passos:"
echo ""
echo "   Opção 1: Copiar arquivos manualmente via SCP do seu computador"
echo "   Opção 2: Importar via interface web do Grafana (colar JSON)"
echo "   Opção 3: Criar dashboards diretamente no Grafana UI"
echo ""
echo "   Para importar via web:"
echo "   1. Acesse: http://192.168.10.16:30000 (ou via port-forward)"
echo "   2. Login: admin / TriSLA2025!"
echo "   3. Ir em: Dashboards > Import"
echo "   4. Colar o conteúdo JSON de cada dashboard"
echo "   5. Salvar"
echo ""
echo "   Ou execute manualmente para criar estrutura:"
echo "   mkdir -p grafana-dashboards"
echo ""




