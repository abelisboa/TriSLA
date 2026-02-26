#!/bin/bash
# Script mestre para corrigir COMPLETAMENTE o backend TriSLA Portal Light
# Corrige CRLF, permissões, ambiente virtual, dependências - TUDO

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "CORREÇÃO COMPLETA - BACKEND TRI-SLA"
echo "=========================================="
echo ""

# 1. Detectar Python
echo -e "${BLUE}[1/8] Detectando Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python não encontrado!${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo -e "${RED}❌ Python 3.10+ necessário. Atual: $PYTHON_MAJOR.$PYTHON_MINOR${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python $PYTHON_VERSION OK${NC}"
echo ""

# 2. Corrigir CRLF em TODOS os arquivos
echo -e "${BLUE}[2/8] Corrigindo line endings (CRLF → LF)...${NC}"
echo "   Corrigindo arquivos .sh..."
find . -name "*.sh" -type f -exec sed -i 's/\r$//' {} + 2>/dev/null || true
echo "   Corrigindo arquivos .py..."
find src -name "*.py" -type f -exec sed -i 's/\r$//' {} + 2>/dev/null || true
echo -e "${GREEN}✅ Line endings corrigidos${NC}"
echo ""

# 3. Garantir shebang em scripts
echo -e "${BLUE}[3/8] Verificando shebang nos scripts...${NC}"
for script in *.sh; do
    if [ -f "$script" ]; then
        if ! head -1 "$script" | grep -q "^#!/bin/bash"; then
            echo "   Adicionando shebang em $script..."
            sed -i '1i#!/bin/bash' "$script" 2>/dev/null || true
        fi
    fi
done
echo -e "${GREEN}✅ Shebangs verificados${NC}"
echo ""

# 4. Corrigir permissões
echo -e "${BLUE}[4/8] Corrigindo permissões...${NC}"
chmod +x *.sh 2>/dev/null || true
chmod +x scripts/*.sh 2>/dev/null || true
echo -e "${GREEN}✅ Permissões corrigidas${NC}"
echo ""

# 5. Remover venv antigo
echo -e "${BLUE}[5/8] Removendo venv antigo...${NC}"
if [ -d "venv" ]; then
    rm -rf venv
    echo -e "${GREEN}✅ Venv antigo removido${NC}"
else
    echo -e "${GREEN}✅ Nenhum venv antigo${NC}"
fi
echo ""

# 6. Criar novo venv
echo -e "${BLUE}[6/8] Criando novo ambiente virtual...${NC}"
$PYTHON_CMD -m venv venv
echo -e "${GREEN}✅ Venv criado${NC}"
echo ""

# 7. Instalar dependências
echo -e "${BLUE}[7/8] Instalando dependências...${NC}"
source venv/bin/activate 2>/dev/null || . venv/bin/activate 2>/dev/null || true
pip install --upgrade pip setuptools wheel --quiet
pip install -r requirements.txt --quiet
echo -e "${GREEN}✅ Dependências instaladas${NC}"
echo ""

# 8. Validar instalação
echo -e "${BLUE}[8/8] Validando instalação...${NC}"
python -c "from src.main import app; print('✅ App importado com sucesso')" || {
    echo -e "${RED}❌ Erro ao importar app${NC}"
    exit 1
}
echo -e "${GREEN}✅ Validação OK${NC}"
echo ""

echo "=========================================="
echo -e "${GREEN}✅ CORREÇÃO COMPLETA FINALIZADA!${NC}"
echo "=========================================="
echo ""
echo "Backend está pronto! Para iniciar:"
echo "  source venv/bin/activate"
echo "  bash start_backend.sh"
echo ""
