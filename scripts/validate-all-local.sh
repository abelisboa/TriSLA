#!/bin/bash
set -e

# ============================================
# Script de Validação Local Completa - TriSLA
# ============================================

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "=========================================="
echo "🔍 Validação Local Completa - TriSLA"
echo "=========================================="
echo ""

# Verificar se Docker está rodando
if ! docker ps &> /dev/null; then
    echo -e "${RED}❌ Docker não está rodando${NC}"
    echo "   Inicie o Docker Desktop e tente novamente"
    exit 1
fi

# Verificar sintaxe Python
echo -e "${CYAN}📝 Verificando sintaxe Python...${NC}"
echo ""

MODULES=("bc-nssmf" "ml-nsmf" "sem-csmf" "decision-engine" "sla-agent-layer")

for module in "${MODULES[@]}"; do
    echo -n "   Verificando $module... "
    if python3 -m py_compile apps/$module/src/*.py 2>/dev/null; then
        echo -e "${GREEN}✅ OK${NC}"
    else
        echo -e "${RED}❌ Erros encontrados${NC}"
    fi
done

echo ""
echo -e "${CYAN}🐳 Verificando Dockerfiles...${NC}"
echo ""

for module in "${MODULES[@]}"; do
    if [ -f "apps/$module/Dockerfile" ]; then
        echo -e "${GREEN}✅ apps/$module/Dockerfile existe${NC}"
    else
        echo -e "${RED}❌ apps/$module/Dockerfile não encontrado${NC}"
    fi
done

# Verificar se ui-dashboard tem Dockerfile
if [ -f "apps/ui-dashboard/Dockerfile" ]; then
    echo -e "${GREEN}✅ apps/ui-dashboard/Dockerfile existe${NC}"
else
    echo -e "${RED}❌ apps/ui-dashboard/Dockerfile não encontrado${NC}"
fi

echo ""
echo -e "${CYAN}📦 Verificando requirements.txt...${NC}"
echo ""

for module in "${MODULES[@]}"; do
    if [ -f "apps/$module/requirements.txt" ]; then
        echo -e "${GREEN}✅ apps/$module/requirements.txt existe${NC}"
    else
        echo -e "${RED}❌ apps/$module/requirements.txt não encontrado${NC}"
    fi
done

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Validação concluída${NC}"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "  1. Execute: ./scripts/test-all.sh"
echo "  2. Execute: ./scripts/build-all-images.sh"
echo "  3. Commit e push: git add . && git commit -m 'fix: correções finais' && git push"





