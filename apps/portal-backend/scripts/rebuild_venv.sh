#!/bin/bash
# Script de Reconstrução Segura do Ambiente Virtual
# Backend TriSLA Portal
# Python 3.10+ | WSL2 Compatível | Zero Conflitos

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$BACKEND_DIR"

echo "============================================================"
echo "  🔧 RECONSTRUÇÃO DO AMBIENTE VIRTUAL - Backend TriSLA"
echo "============================================================"
echo ""

# Verificar Python
echo "[1/6] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ ERRO: Python 3 não encontrado!"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION encontrado"

# Verificar versão mínima
PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "❌ ERRO: Python 3.10+ é necessário. Versão atual: $PYTHON_VERSION"
    exit 1
fi

echo ""

# Remover venv antigo
echo "[2/6] Removendo ambiente virtual antigo..."
if [ -d "venv" ]; then
    echo "   Removendo diretório venv/..."
    rm -rf venv
    echo "✅ Venv antigo removido"
else
    echo "ℹ️  Nenhum venv antigo encontrado"
fi
echo ""

# Criar novo venv
echo "[3/6] Criando novo ambiente virtual..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ ERRO: Falha ao criar ambiente virtual"
    exit 1
fi
echo "✅ Ambiente virtual criado"
echo ""

# Ativar venv
echo "[4/6] Ativando ambiente virtual..."
source venv/bin/activate
echo "✅ Ambiente virtual ativado"
echo ""

# Atualizar pip
echo "[5/6] Atualizando pip, setuptools e wheel..."
pip install --upgrade pip setuptools wheel --quiet
echo "✅ Pip atualizado"
echo ""

# Instalar dependências
echo "[6/6] Instalando dependências com constraints..."
echo "   Isso pode levar alguns minutos..."
echo ""

if [ -f "constraints.txt" ]; then
    echo "   Usando constraints.txt para garantir versões compatíveis..."
    pip install -r requirements.txt --constraint constraints.txt
else
    echo "   ⚠️  constraints.txt não encontrado. Instalando apenas requirements.txt..."
    pip install -r requirements.txt
fi

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ ERRO: Falha ao instalar dependências"
    echo ""
    echo "Tente:"
    echo "  1. Verificar conexão com internet"
    echo "  2. Limpar cache: pip cache purge"
    echo "  3. Verificar versão do Python: python3 --version"
    exit 1
fi

echo ""
echo "✅ Dependências instaladas com sucesso"
echo ""

# Verificar módulos essenciais
echo "============================================================"
echo "  🔍 VERIFICAÇÃO DE MÓDULOS ESSENCIAIS"
echo "============================================================"
echo ""

python3 - <<'EOF'
import sys
import importlib

modules_to_check = [
    ("fastapi", "FastAPI"),
    ("uvicorn", "Uvicorn"),
    ("opentelemetry", "OpenTelemetry API"),
    ("opentelemetry.api", "OpenTelemetry API Module"),
    ("opentelemetry.sdk", "OpenTelemetry SDK"),
    ("opentelemetry.instrumentation.fastapi", "OpenTelemetry FastAPI Instrumentation"),
    ("opentelemetry.instrumentation.httpx", "OpenTelemetry HTTPX Instrumentation"),
    ("sqlalchemy", "SQLAlchemy"),
    ("pydantic", "Pydantic"),
    ("httpx", "HTTPX"),
]

failed = []
for module_name, display_name in modules_to_check:
    try:
        importlib.import_module(module_name)
        print(f"✅ {display_name:40s} ({module_name})")
    except ImportError as e:
        print(f"❌ {display_name:40s} ({module_name}): {e}")
        failed.append((module_name, display_name))

if failed:
    print("\n❌ Alguns módulos não puderam ser importados!")
    for module_name, display_name in failed:
        print(f"   - {display_name} ({module_name})")
    sys.exit(1)
else:
    print("\n✅ Todos os módulos essenciais estão disponíveis!")
    print("\n🎯 Ambiente pronto para uso!")
EOF

CHECK_RESULT=$?

if [ $CHECK_RESULT -ne 0 ]; then
    echo ""
    echo "❌ ERRO: Verificação de módulos falhou"
    exit 1
fi

echo ""
echo "============================================================"
echo "  ✅ RECONSTRUÇÃO CONCLUÍDA COM SUCESSO!"
echo "============================================================"
echo ""
echo "📋 Próximos passos:"
echo ""
echo "1. Ativar o ambiente virtual:"
echo "   source venv/bin/activate"
echo ""
echo "2. Iniciar o backend:"
echo "   python3 run.py"
echo ""
echo "   Ou use o portal manager:"
echo "   bash ../../scripts/portal_manager.sh"
echo ""
echo "3. Verificar saúde do backend:"
echo "   curl http://127.0.0.1:8001/api/v1/health"
echo ""
echo "============================================================"
