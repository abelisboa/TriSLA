#!/bin/bash
# Script para iniciar backend TriSLA Portal Light
# Valida tudo antes de iniciar e usa reload seguro para WSL2

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "START BACKEND - TRI-SLA PORTAL LIGHT"
echo "=========================================="
echo ""

# 1. Verificar se venv existe, se não, criar
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Venv não encontrado. Criando...${NC}"
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}❌ Python não encontrado!${NC}"
        exit 1
    fi
    $PYTHON_CMD -m venv venv
    source venv/bin/activate 2>/dev/null || . venv/bin/activate 2>/dev/null
    pip install --upgrade pip setuptools wheel --quiet --disable-pip-version-check
    pip install -r requirements.txt --quiet --disable-pip-version-check
    echo -e "${GREEN}✅ Venv criado e dependências instaladas${NC}"
    echo ""
fi

# 2. Ativar venv
echo -e "${BLUE}[1/4] Ativando ambiente virtual...${NC}"
source venv/bin/activate 2>/dev/null || . venv/bin/activate 2>/dev/null || {
    echo -e "${RED}❌ Erro ao ativar venv${NC}"
    echo -e "${YELLOW}Execute: bash setup_backend.sh${NC}"
    exit 1
}
echo -e "${GREEN}✅ Venv ativado${NC}"
echo ""

# 3. Verificar arquivos essenciais
echo -e "${BLUE}[2/4] Verificando arquivos essenciais...${NC}"
ESSENTIAL_FILES=("src/main.py" "src/config.py" "src/routers/sla.py" "src/services/nasp.py" "src/schemas/sla.py")
MISSING_FILES=0
for file in "${ESSENTIAL_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Arquivo não encontrado: $file${NC}"
        MISSING_FILES=1
    fi
done

if [ $MISSING_FILES -eq 1 ]; then
    echo -e "${RED}❌ Arquivos essenciais faltando!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Todos os arquivos encontrados${NC}"
echo ""

# 4. Validar imports
echo -e "${BLUE}[3/4] Validando imports...${NC}"
python -c "from src.main import app; print('✅ App OK')" 2>/dev/null || {
    echo -e "${RED}❌ Erro ao importar app!${NC}"
    echo -e "${YELLOW}Execute: bash setup_backend.sh para recriar ambiente${NC}"
    exit 1
}
echo -e "${GREEN}✅ Imports OK${NC}"
echo ""

# 5. Iniciar servidor
echo -e "${BLUE}[4/4] Iniciando servidor...${NC}"
echo ""
echo "=========================================="
echo -e "${GREEN}🚀 BACKEND INICIANDO${NC}"
echo "=========================================="
echo ""
echo "Backend disponível em:"
echo "  URL: http://localhost:8001"
echo "  Health: http://localhost:8001/health"
echo "  API: http://localhost:8001/api/v1"
echo ""
echo "Pressione Ctrl+C para parar"
echo ""
echo "----------------------------------------"
echo ""

# Configurar variáveis de ambiente para WSL2
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Iniciar uvicorn com reload seguro para WSL2
exec uvicorn src.main:app \
    --host 0.0.0.0 \
    --port 8001 \
    --reload \
    --reload-dir src \
    --log-level info \
    --access-log

