#!/bin/bash
# ============================================
# Script de Validação da Infraestrutura NASP
# ============================================
# Valida todos os requisitos da infraestrutura NASP para o TriSLA
# ============================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

echo "🔍 Validando infraestrutura NASP para TriSLA..."
echo ""

# Carregar variáveis de ambiente
if [ -f scripts/trisla_nasp_env.sh ]; then
    source scripts/trisla_nasp_env.sh
else
    echo -e "${YELLOW}⚠️  Script trisla_nasp_env.sh não encontrado. Usando valores padrão.${NC}"
    PRIMARY_IFACE="my5g"
    PRIMARY_IP="192.168.10.16"
fi

# 1. Validar cluster Kubernetes
echo "1️⃣ Validando cluster Kubernetes..."
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl não encontrado${NC}"
    ERRORS=$((ERRORS + 1))
else
    if kubectl cluster-info &> /dev/null; then
        echo -e "${GREEN}✅ kubectl configurado e conectado${NC}"
        
        # Verificar nós
        NODE_COUNT=$(kubectl get nodes --no-headers 2>/dev/null | wc -l)
        CONTROL_PLANE_COUNT=$(kubectl get nodes -l node-role.kubernetes.io/control-plane --no-headers 2>/dev/null | wc -l)
        WORKER_COUNT=$(kubectl get nodes -l '!node-role.kubernetes.io/control-plane' --no-headers 2>/dev/null | wc -l)
        
        echo "   Nós totais: $NODE_COUNT"
        echo "   Control-plane: $CONTROL_PLANE_COUNT"
        echo "   Workers: $WORKER_COUNT"
        
        if [ "$CONTROL_PLANE_COUNT" -ge 2 ] && [ "$WORKER_COUNT" -ge 1 ]; then
            echo -e "${GREEN}✅ Topologia do cluster OK (2+ control-plane, 1+ worker)${NC}"
        else
            echo -e "${RED}❌ Topologia do cluster insuficiente (mínimo: 2 control-plane + 1 worker)${NC}"
            ERRORS=$((ERRORS + 1))
        fi
    else
        echo -e "${RED}❌ Não foi possível conectar ao cluster${NC}"
        ERRORS=$((ERRORS + 1))
    fi
fi
echo ""

# 2. Validar CNI Calico
echo "2️⃣ Validando CNI Calico..."
CALICO_PODS=$(kubectl get pods -n kube-system -l k8s-app=calico-node --no-headers 2>/dev/null | wc -l)
if [ "$CALICO_PODS" -gt 0 ]; then
    READY_CALICO=$(kubectl get pods -n kube-system -l k8s-app=calico-node --no-headers 2>/dev/null | grep -c "Running" || true)
    if [ "$READY_CALICO" -eq "$CALICO_PODS" ]; then
        echo -e "${GREEN}✅ Calico OK ($CALICO_PODS pods rodando)${NC}"
    else
        echo -e "${YELLOW}⚠️  Calico presente mas alguns pods não estão Running${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${RED}❌ Calico não encontrado${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 3. Validar CoreDNS
echo "3️⃣ Validando CoreDNS..."
COREDNS_PODS=$(kubectl get pods -n kube-system -l k8s-app=kube-dns --no-headers 2>/dev/null | wc -l)
if [ "$COREDNS_PODS" -gt 0 ]; then
    echo -e "${GREEN}✅ CoreDNS OK ($COREDNS_PODS pods)${NC}"
else
    echo -e "${RED}❌ CoreDNS não encontrado${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 4. Validar StorageClass
echo "4️⃣ Validar StorageClass..."
STORAGE_CLASSES=$(kubectl get storageclass --no-headers 2>/dev/null | wc -l)
if [ "$STORAGE_CLASSES" -gt 0 ]; then
    echo -e "${GREEN}✅ StorageClass configurado ($STORAGE_CLASSES encontrados)${NC}"
    kubectl get storageclass
else
    echo -e "${RED}❌ Nenhum StorageClass configurado${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 5. Validar recursos dos nós
echo "5️⃣ Validando recursos dos nós..."
kubectl get nodes -o custom-columns=NAME:.metadata.name,CPU:.status.capacity.cpu,RAM:.status.capacity.memory --no-headers | while read -r line; do
    NODE_NAME=$(echo "$line" | awk '{print $1}')
    CPU=$(echo "$line" | awk '{print $2}')
    RAM=$(echo "$line" | awk '{print $3}')
    echo "   $NODE_NAME: CPU=$CPU, RAM=$RAM"
done
echo ""

# 6. Validar DNS interno
echo "6️⃣ Validando DNS interno..."
if kubectl run -it --rm --restart=Never test-dns --image=busybox -- nslookup kubernetes.default &> /dev/null; then
    echo -e "${GREEN}✅ DNS interno funcional${NC}"
    kubectl delete pod test-dns --ignore-not-found=true &> /dev/null
else
    echo -e "${RED}❌ DNS interno não funcional${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 7. Validar Helm
echo "7️⃣ Validando Helm..."
if ! command -v helm &> /dev/null; then
    echo -e "${RED}❌ Helm não encontrado${NC}"
    ERRORS=$((ERRORS + 1))
else
    HELM_VERSION=$(helm version --short 2>/dev/null | head -n1)
    echo -e "${GREEN}✅ Helm instalado: $HELM_VERSION${NC}"
fi
echo ""

# 8. Validar acesso ao GHCR
echo "8️⃣ Validando acesso ao GHCR..."
if [ -n "$GHCR_TOKEN" ] && [ -n "$GHCR_USER" ]; then
    echo -e "${GREEN}✅ Variáveis GHCR configuradas${NC}"
else
    echo -e "${YELLOW}⚠️  Variáveis GHCR não configuradas (GHCR_TOKEN, GHCR_USER)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Resumo
echo "=========================================="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ Validação concluída: Tudo OK!${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Validação concluída com $WARNINGS aviso(s)${NC}"
    exit 0
else
    echo -e "${RED}❌ Validação falhou: $ERRORS erro(s), $WARNINGS aviso(s)${NC}"
    exit 1
fi

