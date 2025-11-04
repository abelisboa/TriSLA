#!/bin/bash
# Script para copiar arquivos do Windows para WSL
# Uso: ./scripts-wsl/copy-from-windows.sh

set -e

WINDOWS_PATH="/mnt/c/Users/USER/Documents/trisla-deploy/trisla-dashboard-local"
WSL_PATH="$HOME/trisla-dashboard-local"

echo "📋 Copiando arquivos do Windows para WSL..."
echo ""
echo "   Origem: $WINDOWS_PATH"
echo "   Destino: $WSL_PATH"
echo ""

# Verificar se o caminho do Windows existe
if [ ! -d "$WINDOWS_PATH" ]; then
    echo "❌ Caminho do Windows não encontrado: $WINDOWS_PATH"
    echo ""
    echo "Por favor, ajuste o caminho no script ou copie manualmente:"
    echo "   cp -r /mnt/c/Users/USER/Documents/trisla-deploy/trisla-dashboard-local ~/trisla-dashboard-local"
    exit 1
fi

# Criar diretório de destino se não existir
mkdir -p "$WSL_PATH"

# Copiar arquivos (excluindo node_modules e venv)
echo "   Copiando arquivos..."
rsync -av --exclude='node_modules' --exclude='venv' --exclude='.git' \
    "$WINDOWS_PATH/" "$WSL_PATH/"

echo ""
echo "✅ Arquivos copiados com sucesso!"
echo ""
echo "Próximo passo:"
echo "   cd ~/trisla-dashboard-local"
echo "   ./scripts-wsl/install-dependencies.sh"





