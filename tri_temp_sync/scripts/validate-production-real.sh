#!/bin/bash
# ============================================
# Validação de Produção Real
# ============================================
# Valida que o TriSLA está configurado para produção real
# ============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

echo "🔍 Validando configuração de PRODUÇÃO REAL..."
echo ""

# 1. Verificar ConfigMap
echo "1️⃣ Verificando ConfigMap..."
SIMULATION_MODE=$(kubectl get configmap trisla-config -n trisla -o jsonpath='{.data.production\.simulationMode}' 2>/dev/null || echo "")
USE_REAL_SERVICES=$(kubectl get configmap trisla-config -n trisla -o jsonpath='{.data.production\.useRealServices}' 2>/dev/null || echo "")
EXECUTE_REAL_ACTIONS=$(kubectl get configmap trisla-config -n trisla -o jsonpath='{.data.production\.executeRealActions}' 2>/dev/null || echo "")

if [ "$SIMULATION_MODE" == "false" ] && [ "$USE_REAL_SERVICES" == "true" ] && [ "$EXECUTE_REAL_ACTIONS" == "true" ]; then
    echo -e "${GREEN}✅ ConfigMap configurado para produção real${NC}"
else
    echo -e "${RED}❌ ConfigMap NÃO está configurado para produção real${NC}"
    echo "   simulationMode: $SIMULATION_MODE (deve ser 'false')"
    echo "   useRealServices: $USE_REAL_SERVICES (deve ser 'true')"
    echo "   executeRealActions: $EXECUTE_REAL_ACTIONS (deve ser 'true')"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 2. Verificar variáveis de ambiente dos pods
echo "2️⃣ Verificando variáveis de ambiente..."
PODS=$(kubectl get pods -n trisla -l app.kubernetes.io/part-of=trisla -o name)
for pod in $PODS; do
    PROD_ENV=$(kubectl get $pod -n trisla -o jsonpath='{.spec.containers[0].env[?(@.name=="PRODUCTION_MODE")].value}' 2>/dev/null || echo "")
    if [ "$PROD_ENV" == "true" ]; then
        echo -e "${GREEN}✅ $pod configurado para produção${NC}"
    else
        echo -e "${YELLOW}⚠️  $pod não tem PRODUCTION_MODE=true${NC}"
    fi
done
echo ""

# 3. Verificar conectividade com NASP real
echo "3️⃣ Verificando conectividade com NASP real..."
if kubectl exec -n trisla deployment/trisla-nasp-adapter -- curl -s http://ran-controller.nasp:8080/health &> /dev/null; then
    echo -e "${GREEN}✅ Conectividade com NASP real OK${NC}"
else
    echo -e "${RED}❌ Falha na conectividade com NASP real${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Resumo
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Validação de produção real: TUDO OK!${NC}"
    exit 0
else
    echo -e "${RED}❌ Validação falhou: $ERRORS erro(s)${NC}"
    exit 1
fi

