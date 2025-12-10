#!/bin/bash
# Script de validação completa do backend
# Valida tudo antes de iniciar

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0

check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1${NC}"
        ((ERRORS++))
        return 1
    fi
}

echo "=========================================="
echo "VALIDAÇÃO COMPLETA - BACKEND"
echo "=========================================="
echo ""

echo -e "${BLUE}[1] Arquivos essenciais...${NC}"
[ -f "src/main.py" ] && check "src/main.py existe" || check "src/main.py NÃO existe"
[ -f "src/config.py" ] && check "src/config.py existe" || check "src/config.py NÃO existe"
[ -f "src/routers/sla.py" ] && check "src/routers/sla.py existe" || check "src/routers/sla.py NÃO existe"
[ -f "src/services/nasp.py" ] && check "src/services/nasp.py existe" || check "src/services/nasp.py NÃO existe"
[ -f "src/schemas/sla.py" ] && check "src/schemas/sla.py existe" || check "src/schemas/sla.py NÃO existe"
[ -f "requirements.txt" ] && check "requirements.txt existe" || check "requirements.txt NÃO existe"
echo ""

echo -e "${BLUE}[2] Ambiente virtual...${NC}"
if [ -d "venv" ]; then
    check "Venv existe"
    if [ -f "venv/bin/activate" ] || [ -f "venv/Scripts/activate" ]; then
        check "Script de ativação existe"
        source venv/bin/activate 2>/dev/null || . venv/bin/activate 2>/dev/null || true
    else
        check "Script de ativação NÃO existe" && ((ERRORS++))
    fi
else
    check "Venv NÃO existe (execute corrigir_tudo.sh)" && ((ERRORS++))
fi
echo ""

if [ -d "venv" ]; then
    source venv/bin/activate 2>/dev/null || . venv/bin/activate 2>/dev/null || true
    
    echo -e "${BLUE}[3] Dependências Python...${NC}"
    python -c "import fastapi" 2>/dev/null && check "FastAPI instalado" || check "FastAPI NÃO instalado"
    python -c "import uvicorn" 2>/dev/null && check "Uvicorn instalado" || check "Uvicorn NÃO instalado"
    python -c "import httpx" 2>/dev/null && check "httpx instalado" || check "httpx NÃO instalado"
    python -c "from pydantic_settings import BaseSettings" 2>/dev/null && check "pydantic-settings instalado" || check "pydantic-settings NÃO instalado"
    echo ""
    
    echo -e "${BLUE}[4] Imports críticos...${NC}"
    python -c "from src.config import settings" 2>/dev/null && check "src.config OK" || check "src.config FALHOU"
    python -c "from src.schemas.sla import SLASubmitResponse" 2>/dev/null && check "src.schemas.sla OK" || check "src.schemas.sla FALHOU"
    python -c "from src.services.nasp import NASPService" 2>/dev/null && check "src.services.nasp OK" || check "src.services.nasp FALHOU"
    python -c "from src.routers.sla import router" 2>/dev/null && check "src.routers.sla OK" || check "src.routers.sla FALHOU"
    python -c "from src.main import app" 2>/dev/null && check "src.main OK" || check "src.main FALHOU"
    echo ""
fi

echo -e "${BLUE}[5] Scripts...${NC}"
[ -x "setup_backend.sh" ] && check "setup_backend.sh executável" || check "setup_backend.sh NÃO executável"
[ -x "start_backend.sh" ] && check "start_backend.sh executável" || check "start_backend.sh NÃO executável"
[ -x "test_backend.sh" ] && check "test_backend.sh executável" || check "test_backend.sh NÃO executável"
[ -x "corrigir_tudo.sh" ] && check "corrigir_tudo.sh executável" || check "corrigir_tudo.sh NÃO executável"
echo ""

echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ VALIDAÇÃO COMPLETA - TUDO OK!${NC}"
    echo "=========================================="
    echo ""
    echo "Backend pronto para iniciar:"
    echo "  source venv/bin/activate"
    echo "  bash start_backend.sh"
    echo ""
    exit 0
else
    echo -e "${RED}❌ VALIDAÇÃO COM ERROS ($ERRORS)${NC}"
    echo "=========================================="
    echo ""
    echo "Execute para corrigir:"
    echo "  bash corrigir_tudo.sh"
    echo ""
    exit 1
fi
