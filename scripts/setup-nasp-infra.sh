#!/bin/bash
# ============================================
# Script de Configuração da Infraestrutura NASP
# ============================================
# Configura todos os componentes necessários da infraestrutura NASP
# ============================================

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🚀 Configurando infraestrutura NASP para TriSLA..."
echo ""

# Carregar variáveis
if [ -f scripts/trisla_nasp_env.sh ]; then
    source scripts/trisla_nasp_env.sh
fi

NAMESPACE="trisla"

# 1. Criar namespace
echo "1️⃣ Criando namespace '$NAMESPACE'..."
if kubectl get namespace "$NAMESPACE" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Namespace '$NAMESPACE' já existe${NC}"
else
    kubectl create namespace "$NAMESPACE"
    echo -e "${GREEN}✅ Namespace '$NAMESPACE' criado${NC}"
fi
echo ""

# 2. Configurar secret do GHCR
echo "2️⃣ Configurando secret do GHCR..."
if [ -z "$GHCR_TOKEN" ] || [ -z "$GHCR_USER" ]; then
    echo -e "${YELLOW}⚠️  Variáveis GHCR não configuradas. Pulando criação do secret.${NC}"
    echo "   Configure GHCR_TOKEN e GHCR_USER e execute:"
    echo "   kubectl create secret docker-registry ghcr-secret \\"
    echo "     --docker-server=ghcr.io \\"
    echo "     --docker-username=\$GHCR_USER \\"
    echo "     --docker-password=\$GHCR_TOKEN \\"
    echo "     --docker-email=abelisboa@gmail.com \\"
    echo "     -n $NAMESPACE"
else
    if kubectl get secret ghcr-secret -n "$NAMESPACE" &> /dev/null; then
        echo -e "${YELLOW}⚠️  Secret 'ghcr-secret' já existe${NC}"
    else
        kubectl create secret docker-registry ghcr-secret \
            --docker-server=ghcr.io \
            --docker-username="$GHCR_USER" \
            --docker-password="$GHCR_TOKEN" \
            --docker-email=abelisboa@gmail.com \
            -n "$NAMESPACE"
        echo -e "${GREEN}✅ Secret 'ghcr-secret' criado${NC}"
    fi
fi
echo ""

# 3. Validar StorageClass
echo "3️⃣ Verificando StorageClass..."
STORAGE_CLASS=$(kubectl get storageclass -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
if [ -n "$STORAGE_CLASS" ]; then
    echo -e "${GREEN}✅ StorageClass disponível: $STORAGE_CLASS${NC}"
else
    echo -e "${YELLOW}⚠️  Nenhum StorageClass encontrado. Configure um StorageClass antes do deploy.${NC}"
fi
echo ""

# 4. Configurar Network Policies (se Calico estiver disponível)
echo "4️⃣ Verificando suporte a Network Policies..."
if kubectl get pods -n kube-system -l k8s-app=calico-node --no-headers &> /dev/null; then
    echo -e "${GREEN}✅ Calico detectado - Network Policies suportadas${NC}"
else
    echo -e "${YELLOW}⚠️  Calico não detectado - Network Policies podem não funcionar${NC}"
fi
echo ""

# 5. Verificar recursos disponíveis
echo "5️⃣ Recursos disponíveis no cluster:"
kubectl top nodes 2>/dev/null || echo "   (métricas não disponíveis - instale metrics-server)"
echo ""

echo "=========================================="
echo -e "${GREEN}✅ Configuração da infraestrutura concluída!${NC}"
echo ""
echo "📋 Próximos passos:"
echo "  1. Executar: ./scripts/validate-nasp-infra.sh"
echo "  2. Revisar: configs/generated/trisla_values_autogen.yaml"
echo "  3. Configurar: configs/generated/inventory_autogen.ini"
echo "  4. Prosseguir com deploy do TriSLA"

