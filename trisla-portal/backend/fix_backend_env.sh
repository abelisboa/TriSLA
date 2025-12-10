#!/bin/bash
# Script para corrigir ambiente do backend TriSLA Portal Light
# Recria venv, instala dependências corretas, corrige problemas comuns

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "FIX BACKEND ENVIRONMENT - TRI-SLA PORTAL"
echo "=========================================="
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Detectar Python
echo -e "${YELLOW}[1/7] Detectando Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version 2>&1)
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version 2>&1)
else
    echo -e "${RED}❌ Python não encontrado!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python encontrado: $PYTHON_VERSION${NC}"
echo ""

# 2. Verificar versão Python (deve ser 3.10+)
echo -e "${YELLOW}[2/7] Verificando versão Python...${NC}"
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo -e "${RED}❌ Python 3.10+ é necessário. Versão atual: $PYTHON_MAJOR.$PYTHON_MINOR${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Versão Python OK: $PYTHON_MAJOR.$PYTHON_MINOR${NC}"
echo ""

# 3. Remover venv antigo se existir
echo -e "${YELLOW}[3/7] Removendo venv antigo...${NC}"
if [ -d "venv" ]; then
    echo "   Removendo diretório venv..."
    rm -rf venv
    echo -e "${GREEN}✅ Venv antigo removido${NC}"
else
    echo -e "${GREEN}✅ Nenhum venv antigo encontrado${NC}"
fi
echo ""

# 4. Criar novo venv
echo -e "${YELLOW}[4/7] Criando novo ambiente virtual...${NC}"
$PYTHON_CMD -m venv venv
echo -e "${GREEN}✅ Ambiente virtual criado${NC}"
echo ""

# 5. Ativar venv e atualizar pip
echo -e "${YELLOW}[5/7] Ativando venv e atualizando pip...${NC}"
source venv/bin/activate || . venv/bin/activate
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✅ Pip atualizado${NC}"
echo ""

# 6. Instalar dependências
echo -e "${YELLOW}[6/7] Instalando dependências...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dependências instaladas${NC}"
else
    echo -e "${RED}❌ requirements.txt não encontrado!${NC}"
    exit 1
fi
echo ""

# 7. Verificar instalação
echo -e "${YELLOW}[7/7] Verificando instalação...${NC}"
python -c "import fastapi; print(f'✅ FastAPI: {fastapi.__version__}')"
python -c "import uvicorn; print(f'✅ Uvicorn: {uvicorn.__version__}')"
python -c "import httpx; print(f'✅ httpx: {httpx.__version__}')"
python -c "import pydantic; print(f'✅ Pydantic: {pydantic.__version__}')"
python -c "from pydantic_settings import BaseSettings; print('✅ pydantic-settings: OK')"
python -c "import dotenv; print('✅ python-dotenv: OK')"
python -c "import prometheus_client; print('✅ prometheus-client: OK')"
echo ""

# 8. Verificar imports críticos
echo -e "${YELLOW}[EXTRA] Verificando imports críticos...${NC}"
python -c "from src.config import settings; print('✅ src.config: OK')" || echo -e "${RED}❌ Erro ao importar src.config${NC}"
python -c "from src.schemas.sla import SLASubmitResponse; print('✅ src.schemas.sla: OK')" || echo -e "${RED}❌ Erro ao importar src.schemas.sla${NC}"
python -c "from src.services.nasp import NASPService; print('✅ src.services.nasp: OK')" || echo -e "${RED}❌ Erro ao importar src.services.nasp${NC}"
python -c "from src.routers.sla import router; print('✅ src.routers.sla: OK')" || echo -e "${RED}❌ Erro ao importar src.routers.sla${NC}"
echo ""

echo "=========================================="
echo -e "${GREEN}✅ AMBIENTE CORRIGIDO COM SUCESSO!${NC}"
echo "=========================================="
echo ""
echo "Para ativar o ambiente virtual:"
echo "  source venv/bin/activate"
echo ""
echo "Para iniciar o backend:"
echo "  uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload"
echo ""

