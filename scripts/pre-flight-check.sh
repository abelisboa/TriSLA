#!/bin/bash
# ============================================
# Script Pré-Flight - Validação Completa TriSLA
# ============================================
# Valida todos os requisitos antes do deploy
# ============================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Arquivo de relatório JSON
REPORT_FILE="pre-flight-report.json"
ERRORS=0
WARNINGS=0
CHECKS=()

# Função para adicionar check
add_check() {
    local name=$1
    local status=$2
    local message=$3
    
    CHECKS+=("{\"name\":\"$name\",\"status\":\"$status\",\"message\":\"$message\"}")
    
    if [ "$status" == "ERROR" ]; then
        ERRORS=$((ERRORS + 1))
    elif [ "$status" == "WARNING" ]; then
        WARNINGS=$((WARNINGS + 1))
    fi
}

# Função para gerar relatório JSON
generate_report() {
    echo "{" > "$REPORT_FILE"
    echo "  \"timestamp\": \"$(date -Iseconds)\"," >> "$REPORT_FILE"
    echo "  \"errors\": $ERRORS," >> "$REPORT_FILE"
    echo "  \"warnings\": $WARNINGS," >> "$REPORT_FILE"
    echo "  \"checks\": [" >> "$REPORT_FILE"
    
    local first=true
    for check in "${CHECKS[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            echo "," >> "$REPORT_FILE"
        fi
        echo "    $check" >> "$REPORT_FILE"
    done
    
    echo "  ]" >> "$REPORT_FILE"
    echo "}" >> "$REPORT_FILE"
}

echo "🔍 Executando Pré-Flight Checks do TriSLA..."
echo ""

# 1. Verificar versão do Kubernetes
echo "1️⃣ Verificando versão do Kubernetes..."
if command -v kubectl &> /dev/null; then
    K8S_VERSION=$(kubectl version --client --short 2>/dev/null | awk '{print $3}' | cut -d'v' -f2)
    K8S_MAJOR=$(echo "$K8S_VERSION" | cut -d'.' -f1)
    K8S_MINOR=$(echo "$K8S_VERSION" | cut -d'.' -f2)
    
    if [ "$K8S_MAJOR" -ge 1 ] && [ "$K8S_MINOR" -ge 24 ]; then
        echo -e "${GREEN}✅ Kubernetes versão OK: $K8S_VERSION${NC}"
        add_check "kubernetes_version" "OK" "Versão $K8S_VERSION (>= 1.24)"
    else
        echo -e "${RED}❌ Kubernetes versão insuficiente: $K8S_VERSION (mínimo: 1.24)${NC}"
        add_check "kubernetes_version" "ERROR" "Versão $K8S_VERSION insuficiente (mínimo: 1.24)"
    fi
else
    echo -e "${RED}❌ kubectl não encontrado${NC}"
    add_check "kubernetes_version" "ERROR" "kubectl não instalado"
fi
echo ""

# 2. Verificar certificados
echo "2️⃣ Verificando certificados do cluster..."
if kubectl get --raw /healthz &> /dev/null; then
    echo -e "${GREEN}✅ Certificados do cluster válidos${NC}"
    add_check "cluster_certificates" "OK" "Certificados válidos"
else
    echo -e "${RED}❌ Erro ao acessar cluster (certificados inválidos?)${NC}"
    add_check "cluster_certificates" "ERROR" "Certificados inválidos ou cluster inacessível"
fi
echo ""

# 3. Verificar DNS interno
echo "3️⃣ Verificando DNS interno..."
if kubectl run -it --rm --restart=Never test-dns-$(date +%s) --image=busybox -- nslookup kubernetes.default &> /dev/null; then
    echo -e "${GREEN}✅ DNS interno funcional${NC}"
    add_check "dns_internal" "OK" "DNS interno funcional"
    kubectl delete pod test-dns-* --ignore-not-found=true &> /dev/null
else
    echo -e "${RED}❌ DNS interno não funcional${NC}"
    add_check "dns_internal" "ERROR" "DNS interno não funcional"
fi
echo ""

# 4. Verificar autenticação GHCR
echo "4️⃣ Verificando autenticação GHCR..."
if [ -n "$GHCR_TOKEN" ] && [ -n "$GHCR_USER" ]; then
    # Tentar login
    if echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin &> /dev/null; then
        echo -e "${GREEN}✅ Autenticação GHCR OK${NC}"
        add_check "ghcr_authentication" "OK" "Autenticação GHCR bem-sucedida"
    else
        echo -e "${RED}❌ Falha na autenticação GHCR${NC}"
        add_check "ghcr_authentication" "ERROR" "Falha na autenticação GHCR"
    fi
else
    echo -e "${YELLOW}⚠️  Variáveis GHCR não configuradas${NC}"
    add_check "ghcr_authentication" "WARNING" "Variáveis GHCR não configuradas"
fi
echo ""

# 5. Verificar NetworkPolicy (suporte)
echo "5️⃣ Verificando suporte a NetworkPolicy..."
if kubectl get crd networkpolicies.crd.projectcalico.org &> /dev/null || kubectl api-resources | grep -q networkpolicies; then
    echo -e "${GREEN}✅ NetworkPolicy suportado${NC}"
    add_check "networkpolicy_support" "OK" "NetworkPolicy suportado"
else
    echo -e "${YELLOW}⚠️  NetworkPolicy pode não ser suportado${NC}"
    add_check "networkpolicy_support" "WARNING" "NetworkPolicy pode não ser suportado"
fi
echo ""

# 6. Verificar saúde do Calico
echo "6️⃣ Verificando saúde do Calico..."
CALICO_PODS=$(kubectl get pods -n kube-system -l k8s-app=calico-node --no-headers 2>/dev/null | wc -l)
if [ "$CALICO_PODS" -gt 0 ]; then
    READY_CALICO=$(kubectl get pods -n kube-system -l k8s-app=calico-node --no-headers 2>/dev/null | grep -c "Running" || echo "0")
    if [ "$READY_CALICO" -eq "$CALICO_PODS" ]; then
        echo -e "${GREEN}✅ Calico saudável ($CALICO_PODS/$CALICO_PODS pods Running)${NC}"
        add_check "calico_health" "OK" "Calico saudável ($CALICO_PODS pods)"
    else
        echo -e "${RED}❌ Calico com problemas ($READY_CALICO/$CALICO_PODS pods Running)${NC}"
        add_check "calico_health" "ERROR" "Calico com problemas ($READY_CALICO/$CALICO_PODS pods)"
    fi
else
    echo -e "${RED}❌ Calico não encontrado${NC}"
    add_check "calico_health" "ERROR" "Calico não encontrado"
fi
echo ""

# 7. Verificar Helm
echo "7️⃣ Verificando Helm..."
if command -v helm &> /dev/null; then
    HELM_VERSION=$(helm version --short 2>/dev/null | head -n1)
    HELM_MAJOR=$(echo "$HELM_VERSION" | grep -oP 'v\K\d+' | head -n1)
    if [ "$HELM_MAJOR" -ge 3 ]; then
        echo -e "${GREEN}✅ Helm OK: $HELM_VERSION${NC}"
        add_check "helm_version" "OK" "Helm $HELM_VERSION (>= 3.0)"
    else
        echo -e "${RED}❌ Helm versão insuficiente: $HELM_VERSION (mínimo: 3.0)${NC}"
        add_check "helm_version" "ERROR" "Helm $HELM_VERSION insuficiente (mínimo: 3.0)"
    fi
else
    echo -e "${RED}❌ Helm não encontrado${NC}"
    add_check "helm_version" "ERROR" "Helm não instalado"
fi
echo ""

# 8. Verificar recursos disponíveis
echo "8️⃣ Verificando recursos disponíveis..."
TOTAL_CPU=$(kubectl describe nodes | grep -i "cpu" | grep -oP '\d+(?=m)' | awk '{sum+=$1} END {print sum/1000}')
TOTAL_MEM=$(kubectl describe nodes | grep -i "memory" | grep -oP '\d+(?=Ki)' | head -n1 | awk '{print $1/1024/1024}')
if [ -n "$TOTAL_CPU" ] && [ -n "$TOTAL_MEM" ]; then
    echo "   CPU total: ${TOTAL_CPU} cores"
    echo "   Memória total: ${TOTAL_MEM} GB"
    if (( $(echo "$TOTAL_CPU >= 8" | bc -l) )) && (( $(echo "$TOTAL_MEM >= 16" | bc -l) )); then
        echo -e "${GREEN}✅ Recursos suficientes${NC}"
        add_check "resources" "OK" "Recursos suficientes (CPU: ${TOTAL_CPU} cores, RAM: ${TOTAL_MEM} GB)"
    else
        echo -e "${YELLOW}⚠️  Recursos podem ser insuficientes${NC}"
        add_check "resources" "WARNING" "Recursos podem ser insuficientes"
    fi
else
    echo -e "${YELLOW}⚠️  Não foi possível verificar recursos${NC}"
    add_check "resources" "WARNING" "Não foi possível verificar recursos"
fi
echo ""

# 9. Verificar StorageClass
echo "9️⃣ Verificando StorageClass..."
STORAGE_CLASSES=$(kubectl get storageclass --no-headers 2>/dev/null | wc -l)
if [ "$STORAGE_CLASSES" -gt 0 ]; then
    echo -e "${GREEN}✅ StorageClass configurado ($STORAGE_CLASSES encontrados)${NC}"
    add_check "storageclass" "OK" "$STORAGE_CLASSES StorageClass(es) configurado(s)"
else
    echo -e "${RED}❌ Nenhum StorageClass configurado${NC}"
    add_check "storageclass" "ERROR" "Nenhum StorageClass configurado"
fi
echo ""

# 10. Verificar namespace
echo "🔟 Verificando namespace trisla..."
if kubectl get namespace trisla &> /dev/null; then
    echo -e "${GREEN}✅ Namespace 'trisla' existe${NC}"
    add_check "namespace" "OK" "Namespace 'trisla' existe"
else
    echo -e "${YELLOW}⚠️  Namespace 'trisla' não existe (será criado no deploy)${NC}"
    add_check "namespace" "WARNING" "Namespace 'trisla' não existe"
fi
echo ""

# Gerar relatório
generate_report

# Resumo final
echo "=========================================="
echo "📊 Resumo do Pré-Flight Check:"
echo "   Erros: $ERRORS"
echo "   Avisos: $WARNINGS"
echo "   Relatório: $REPORT_FILE"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ Todos os checks passaram! Pronto para deploy.${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Checks passaram com $WARNINGS aviso(s). Revisar antes do deploy.${NC}"
    exit 0
else
    echo -e "${RED}❌ $ERRORS erro(s) encontrado(s). Corrigir antes do deploy!${NC}"
    echo ""
    echo "Verifique o relatório JSON: $REPORT_FILE"
    exit 1
fi

