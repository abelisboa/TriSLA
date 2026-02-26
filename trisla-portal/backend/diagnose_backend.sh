#!/bin/bash
# Script de diagnóstico completo do backend TriSLA Portal Light
# Identifica problemas comuns e sugere correções

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "DIAGNÓSTICO BACKEND - TRI-SLA PORTAL"
echo "=========================================="
echo ""

ERRORS=0
WARNINGS=0

# Função para reportar erro
report_error() {
    echo -e "${RED}❌ $1${NC}"
    ((ERRORS++))
}

# Função para reportar warning
report_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

# Função para reportar sucesso
report_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

###############################################
# 1. Verificar Python
###############################################
echo -e "${BLUE}[1] Verificando Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version 2>&1)
    report_success "Python encontrado: $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version 2>&1)
    report_success "Python encontrado: $PYTHON_VERSION"
else
    report_error "Python não encontrado!"
    exit 1
fi

PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    report_error "Python 3.10+ é necessário. Versão atual: $PYTHON_MAJOR.$PYTHON_MINOR"
else
    report_success "Versão Python OK: $PYTHON_MAJOR.$PYTHON_MINOR"
fi
echo ""

###############################################
# 2. Verificar arquivos essenciais
###############################################
echo -e "${BLUE}[2] Verificando arquivos essenciais...${NC}"

ESSENTIAL_FILES=(
    "src/main.py"
    "src/config.py"
    "src/routers/sla.py"
    "src/services/nasp.py"
    "src/schemas/sla.py"
    "requirements.txt"
)

for file in "${ESSENTIAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        report_success "$file existe"
    else
        report_error "$file NÃO encontrado!"
    fi
done
echo ""

###############################################
# 3. Verificar ambiente virtual
###############################################
echo -e "${BLUE}[3] Verificando ambiente virtual...${NC}"
if [ -d "venv" ]; then
    report_success "Diretório venv existe"
    
    # Verificar se pode ativar
    if [ -f "venv/bin/activate" ] || [ -f "venv/Scripts/activate" ]; then
        report_success "Script de ativação encontrado"
    else
        report_warning "Script de ativação não encontrado - venv pode estar corrompido"
    fi
else
    report_warning "Diretório venv não existe - será necessário criar"
fi
echo ""

###############################################
# 4. Verificar dependências (se venv existe)
###############################################
echo -e "${BLUE}[4] Verificando dependências...${NC}"
if [ -d "venv" ]; then
    source venv/bin/activate 2>/dev/null || . venv/bin/activate 2>/dev/null || true
    
    REQUIRED_PACKAGES=(
        "fastapi"
        "uvicorn"
        "httpx"
        "pydantic"
        "pydantic_settings"
        "dotenv"
        "prometheus_client"
    )
    
    for package in "${REQUIRED_PACKAGES[@]}"; do
        if python -c "import $package" 2>/dev/null; then
            VERSION=$(python -c "import $package; print(getattr($package, '__version__', 'OK'))" 2>/dev/null || echo "OK")
            report_success "$package: $VERSION"
        else
            report_error "$package não instalado"
        fi
    done
else
    report_warning "Venv não existe - pule esta verificação"
fi
echo ""

###############################################
# 5. Verificar imports críticos
###############################################
echo -e "${BLUE}[5] Verificando imports críticos...${NC}"
if [ -d "venv" ]; then
    source venv/bin/activate 2>/dev/null || . venv/bin/activate 2>/dev/null || true
    
    CRITICAL_IMPORTS=(
        "from src.config import settings"
        "from src.schemas.sla import SLASubmitResponse"
        "from src.services.nasp import NASPService"
        "from src.routers.sla import router"
    )
    
    for import_cmd in "${CRITICAL_IMPORTS[@]}"; do
        if python -c "$import_cmd" 2>/dev/null; then
            report_success "$import_cmd"
        else
            report_error "Falha ao importar: $import_cmd"
        fi
    done
else
    report_warning "Venv não existe - pule esta verificação"
fi
echo ""

###############################################
# 6. Verificar line endings
###############################################
echo -e "${BLUE}[6] Verificando line endings...${NC}"
CRLF_COUNT=$(find src -name "*.py" -type f -exec file {} \; | grep -c "CRLF" || echo "0")
if [ "$CRLF_COUNT" -gt 0 ]; then
    report_warning "$CRLF_COUNT arquivo(s) Python com CRLF - execute fix_line_endings.sh"
else
    report_success "Line endings OK (LF)"
fi
echo ""

###############################################
# 7. Verificar permissões
###############################################
echo -e "${BLUE}[7] Verificando permissões de scripts...${NC}"
SCRIPTS=(
    "fix_backend_env.sh"
    "start_backend.sh"
    "test_backend_routes.sh"
)

for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            report_success "$script é executável"
        else
            report_warning "$script não é executável - execute: chmod +x $script"
        fi
    fi
done
echo ""

###############################################
# Resumo Final
###############################################
echo "=========================================="
echo "RESUMO DO DIAGNÓSTICO"
echo "=========================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ BACKEND OK - Pronto para uso!${NC}"
    echo ""
    echo "Para iniciar:"
    echo "  bash start_backend.sh"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  BACKEND COM AVISOS ($WARNINGS)${NC}"
    echo ""
    echo "Recomendações:"
    if [ ! -d "venv" ]; then
        echo "  - Execute: bash fix_backend_env.sh"
    fi
    if [ "$CRLF_COUNT" -gt 0 ]; then
        echo "  - Execute: bash fix_line_endings.sh"
    fi
else
    echo -e "${RED}❌ BACKEND COM ERROS ($ERRORS erros, $WARNINGS avisos)${NC}"
    echo ""
    echo "Correções necessárias:"
    echo "  1. Execute: bash fix_backend_env.sh"
    echo "  2. Execute: bash fix_line_endings.sh"
    echo "  3. Execute: bash diagnose_backend.sh (novamente)"
fi

echo ""
exit $ERRORS

