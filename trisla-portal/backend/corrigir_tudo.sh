#!/bin/bash
# Script mestre para corrigir TUDO automaticamente
# Corrige CRLF, recria venv, valida imports, garante funcionamento

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "CORREÇÃO COMPLETA - TRI-SLA PORTAL BACKEND"
echo "=========================================="
echo ""

ERRORS=0

step() {
    echo -e "${BLUE}[$1] $2${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    ((ERRORS++))
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

step "1/7" "Corrigindo line endings (CRLF → LF)..."
find . -name "*.sh" -type f -exec sed -i 's/\r$//' {} + 2>/dev/null || true
find src -name "*.py" -type f -exec sed -i 's/\r$//' {} + 2>/dev/null || true
success "Line endings corrigidos"
echo ""

step "2/7" "Corrigindo permissões de scripts..."
chmod +x *.sh 2>/dev/null || true
chmod +x scripts/*.sh 2>/dev/null || true
success "Permissões corrigidas"
echo ""

step "3/7" "Detectando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    error "Python não encontrado!"
    exit 1
fi

PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    error "Python 3.10+ necessário. Atual: $PYTHON_MAJOR.$PYTHON_MINOR"
    exit 1
fi
success "Python $PYTHON_CMD OK ($PYTHON_MAJOR.$PYTHON_MINOR)"
echo ""

step "4/7" "Removendo venv antigo..."
if [ -d "venv" ]; then
    rm -rf venv
    success "Venv antigo removido"
else
    success "Nenhum venv antigo"
fi
echo ""

step "5/7" "Criando novo ambiente virtual..."
$PYTHON_CMD -m venv venv
if [ ! -f "venv/bin/activate" ] && [ ! -f "venv/Scripts/activate" ]; then
    error "Falha ao criar venv"
    exit 1
fi
success "Venv criado"
echo ""

step "6/7" "Ativando venv e instalando dependências..."
source venv/bin/activate 2>/dev/null || . venv/bin/activate 2>/dev/null || {
    error "Erro ao ativar venv"
    exit 1
}

pip install --upgrade pip setuptools wheel --quiet
if [ ! -f "requirements.txt" ]; then
    error "requirements.txt não encontrado!"
    exit 1
fi

pip install -r requirements.txt --quiet
success "Dependências instaladas"
echo ""

step "7/7" "Validando instalação e imports..."
python -c "import fastapi; print('✅ FastAPI OK')" || error "FastAPI falhou"
python -c "import uvicorn; print('✅ Uvicorn OK')" || error "Uvicorn falhou"
python -c "import httpx; print('✅ httpx OK')" || error "httpx falhou"
python -c "from pydantic_settings import BaseSettings; print('✅ pydantic-settings OK')" || error "pydantic-settings falhou"
python -c "from src.config import settings; print('✅ src.config OK')" || error "src.config falhou"
python -c "from src.schemas.sla import SLASubmitResponse; print('✅ src.schemas.sla OK')" || error "src.schemas.sla falhou"
python -c "from src.services.nasp import NASPService; print('✅ src.services.nasp OK')" || error "src.services.nasp falhou"
python -c "from src.routers.sla import router; print('✅ src.routers.sla OK')" || error "src.routers.sla falhou"
python -c "from src.main import app; print('✅ src.main OK')" || error "src.main falhou"
echo ""

echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ CORREÇÃO COMPLETA - SEM ERROS!${NC}"
    echo "=========================================="
    echo ""
    echo "Para iniciar o backend:"
    echo "  source venv/bin/activate"
    echo "  bash start_backend.sh"
    echo ""
    exit 0
else
    echo -e "${RED}❌ CORREÇÃO COM ERROS ($ERRORS)${NC}"
    echo "=========================================="
    exit 1
fi
