#!/bin/bash
# Script simples para instalar dependências do backend TriSLA Portal

BACKEND_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$BACKEND_DIR"

echo "============================================================"
echo "  Instalando Dependências - TriSLA Portal Backend"
echo "============================================================"

if [ ! -f "venv/bin/activate" ]; then
    echo "[ERRO] venv não encontrado. Criando ambiente virtual..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERRO] Falha ao criar venv."
        exit 1
    fi
fi

echo "[INFO] Ativando ambiente virtual..."
source venv/bin/activate

echo "[INFO] Atualizando pip..."
pip install --upgrade pip -q

echo "[INFO] Instalando dependências..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✅ Dependências instaladas com sucesso!"
    echo "============================================================"
    echo ""
    echo "Para iniciar o backend:"
    echo "  source venv/bin/activate"
    echo "  python3 run.py"
    echo ""
else
    echo ""
    echo "============================================================"
    echo "❌ Erro ao instalar dependências"
    echo "============================================================"
    exit 1
fi


