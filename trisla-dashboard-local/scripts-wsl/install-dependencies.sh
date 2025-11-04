#!/bin/bash
# Script para instalar todas as dependências
# Uso: ./scripts-wsl/install-dependencies.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "📦 Instalando dependências do TriSLA Dashboard..."
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale com:"
    echo "   sudo apt update && sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# Verificar se Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Instale com:"
    echo "   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -"
    echo "   sudo apt-get install -y nodejs"
    exit 1
fi

# Verificar se npm está instalado
if ! command -v npm &> /dev/null; then
    echo "❌ npm não encontrado. Instale Node.js (inclui npm)"
    exit 1
fi

echo "✅ Python: $(python3 --version)"
echo "✅ Node.js: $(node --version)"
echo "✅ npm: $(npm --version)"
echo ""

# 1. Backend - Criar venv e instalar dependências
echo "1️⃣ Configurando backend..."
cd "$PROJECT_DIR/backend"

if [ ! -d "venv" ]; then
    echo "   Criando venv..."
    python3 -m venv venv
fi

echo "   Ativando venv..."
source venv/bin/activate

echo "   Atualizando pip..."
pip install --upgrade pip > /dev/null

echo "   Instalando dependências Python..."
pip install -r requirements.txt

echo "   ✅ Backend configurado"
echo ""

# 2. Frontend - Instalar dependências npm
echo "2️⃣ Configurando frontend..."
cd "$PROJECT_DIR/frontend"

echo "   Instalando dependências npm..."
npm install

echo "   ✅ Frontend configurado"
echo ""

echo "✅ Todas as dependências instaladas!"
echo ""
echo "Próximo passo: ./scripts-wsl/start-all.sh"

