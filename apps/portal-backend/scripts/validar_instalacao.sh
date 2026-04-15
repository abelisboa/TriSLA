#!/bin/bash
# Script de Validação Final - Backend TriSLA Portal
# Valida instalação completa e funcionamento do backend

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$BACKEND_DIR"

echo "============================================================"
echo "  ✅ VALIDAÇÃO FINAL - Backend TriSLA Portal"
echo "============================================================"
echo ""

# Verificar se venv existe
if [ ! -d "venv" ]; then
    echo "❌ ERRO: Ambiente virtual não encontrado!"
    echo ""
    echo "Execute primeiro:"
    echo "  bash scripts/rebuild_venv.sh"
    exit 1
fi

# Ativar venv
source venv/bin/activate

# Teste 1: Verificar importações Python
echo "[TESTE 1/4] Verificando importações Python..."
python3 - <<'EOF'
import sys
import importlib

modules = [
    "fastapi",
    "uvicorn",
    "opentelemetry",
    "opentelemetry.api",
    "opentelemetry.sdk",
    "opentelemetry.instrumentation.fastapi",
    "opentelemetry.instrumentation.httpx",
    "sqlalchemy",
    "pydantic",
    "httpx",
]

failed = []
for module in modules:
    try:
        importlib.import_module(module)
        print(f"  ✅ {module}")
    except ImportError as e:
        print(f"  ❌ {module}: {e}")
        failed.append(module)

if failed:
    print(f"\n❌ {len(failed)} módulo(s) falharam na importação")
    sys.exit(1)
else:
    print("\n✅ Todos os módulos importados com sucesso")
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ ERRO: Falha na verificação de importações"
    exit 1
fi

echo ""

# Teste 2: Verificar se o backend pode ser importado
echo "[TESTE 2/4] Verificando importação do backend..."
python3 -c "from src.main import app; print('  ✅ Backend importado com sucesso')" 2>&1
if [ $? -ne 0 ]; then
    echo "  ❌ Falha ao importar backend"
    exit 1
fi
echo ""

# Teste 3: Verificar sintaxe do run.py
echo "[TESTE 3/4] Verificando sintaxe do run.py..."
python3 -m py_compile run.py 2>&1
if [ $? -ne 0 ]; then
    echo "  ❌ Erro de sintaxe em run.py"
    exit 1
else
    echo "  ✅ run.py sem erros de sintaxe"
fi
echo ""

# Teste 4: Verificar estrutura de arquivos
echo "[TESTE 4/4] Verificando estrutura de arquivos..."
REQUIRED_FILES=(
    "requirements.txt"
    "constraints.txt"
    "run.py"
    "src/main.py"
    "src/config.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file não encontrado"
        exit 1
    fi
done

echo ""
echo "============================================================"
echo "  ✅ VALIDAÇÃO CONCLUÍDA COM SUCESSO!"
echo "============================================================"
echo ""
echo "📋 Próximos passos:"
echo ""
echo "1. Iniciar o backend:"
echo "   python3 run.py"
echo ""
echo "   Ou use o portal manager:"
echo "   bash ../../scripts/portal_manager.sh"
echo ""
echo "2. Testar endpoints:"
echo "   curl http://127.0.0.1:8001/api/v1/health"
echo "   curl -I -X OPTIONS http://127.0.0.1:8001/api/v1/modules -H 'Origin: http://localhost:3000'"
echo ""
echo "============================================================"
