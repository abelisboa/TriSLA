#!/bin/bash
# Script para criar túnel SSH para acessar o Portal TriSLA

set -e

echo "🔗 Criando túnel SSH para Portal TriSLA..."
echo ""
echo "Este script criará port-forwarding para:"
echo "  - Frontend: localhost:32001 -> node1:32001"
echo "  - Backend:  localhost:32002 -> node1:32002"
echo ""
echo "⚠️  Certifique-se de que o túnel SSH está configurado corretamente"
echo "   e que você tem acesso ao node1 do cluster NASP"
echo ""

# Verificar se ssh está disponível
if ! command -v ssh &> /dev/null; then
    echo "❌ Erro: SSH não está instalado"
    exit 1
fi

echo "🚀 Iniciando túnel SSH..."
echo "   Pressione Ctrl+C para encerrar o túnel"
echo ""

# Criar túnel SSH
ssh -L 32001:localhost:32001 \
    -L 32002:localhost:32002 \
    porvir5g@node1

echo ""
echo "✅ Túnel SSH encerrado"

