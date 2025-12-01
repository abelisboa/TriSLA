#!/bin/bash
# ============================================
# Setup do Ambiente de Desenvolvimento
# ============================================

set -e

echo "🚀 Configurando ambiente de desenvolvimento..."
echo ""

# Criar ambiente virtual Python
echo "1️⃣ Criando ambiente virtual Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate || source venv/Scripts/activate

# Instalar dependências de desenvolvimento
echo "2️⃣ Instalando dependências..."
pip install --upgrade pip
pip install -r tests/requirements.txt

# Instalar dependências de cada módulo
for module in apps/*/; do
    if [ -f "${module}requirements.txt" ]; then
        echo "   Instalando dependências de ${module}..."
        pip install -r "${module}requirements.txt" || true
    fi
done

echo ""
echo "✅ Ambiente de desenvolvimento configurado!"
echo ""
echo "Para ativar o ambiente virtual:"
echo "  source venv/bin/activate  # Linux/Mac"
echo "  venv\\Scripts\\activate     # Windows"

