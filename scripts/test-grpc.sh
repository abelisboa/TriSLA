#!/bin/bash
set -e

# ============================================
# Script de Teste gRPC - TriSLA
# ============================================

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "🧪 Teste gRPC - TriSLA"
echo "=========================================="
echo ""

# Verificar se grpcurl está instalado
if ! command -v grpcurl &> /dev/null; then
    echo -e "${YELLOW}⚠️  grpcurl não está instalado${NC}"
    echo "   Instale com: brew install grpcurl (macOS) ou go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest"
    exit 1
fi

# Testar SEM-CSMF gRPC (porta 50051)
echo "Testando SEM-CSMF gRPC (localhost:50051)..."
if grpcurl -plaintext localhost:50051 list 2>/dev/null; then
    echo -e "${GREEN}✅ SEM-CSMF gRPC está respondendo${NC}"
    
    # Listar serviços
    echo "   Serviços disponíveis:"
    grpcurl -plaintext localhost:50051 list | sed 's/^/      - /'
else
    echo -e "${RED}❌ SEM-CSMF gRPC não está respondendo${NC}"
fi

echo ""
echo "=========================================="
echo "✅ Testes gRPC concluídos"
echo "=========================================="


