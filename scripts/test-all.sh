#!/bin/bash
set -e

# ============================================
# Script de Teste Completo - TriSLA
# ============================================

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "=========================================="
echo "🧪 Teste Completo - TriSLA"
echo "=========================================="
echo ""

# Verificar se Docker está rodando
if ! docker ps &> /dev/null; then
    echo -e "${RED}❌ Docker não está rodando${NC}"
    exit 1
fi

# Executar todos os testes
echo -e "${CYAN}📦 Testando serviços HTTP...${NC}"
bash scripts/test-local-services.sh

echo ""
echo -e "${CYAN}🌐 Testando gRPC...${NC}"
bash scripts/test-grpc.sh

echo ""
echo -e "${CYAN}🔧 Testando Nginx...${NC}"
bash scripts/test-nginx.sh

echo ""
echo -e "${CYAN}⛓️  Testando Blockchain...${NC}"
bash scripts/test-blockchain.sh

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Todos os testes concluídos${NC}"
echo "=========================================="


