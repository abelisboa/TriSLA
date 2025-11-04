#!/bin/bash
# Diagnosticar estrutura do pod

echo "=========================================="
echo "🔍 Diagnosticando Estrutura do Pod"
echo "=========================================="

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
echo "Pod: $POD_NAME"
echo ""

# 1. Ver containers
echo "1️⃣ Containers no pod:"
kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[*].name}'
echo ""
echo ""

# 2. Ver estrutura de diretórios
echo "2️⃣ Estrutura de diretórios no pod:"
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')
echo "Container: $CONTAINER"
echo ""

echo "Verificando /app:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -la /app 2>/dev/null | head -20
echo ""

echo "Verificando /app/apps:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -la /app/apps 2>/dev/null
echo ""

echo "Verificando /app/apps/api (se existir):"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -la /app/apps/api 2>/dev/null
echo ""

# 3. Verificar PYTHONPATH
echo "3️⃣ Variáveis de ambiente:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- env | grep -E "PYTHONPATH|PWD|PATH" | head -10
echo ""

# 4. Verificar comando rodando
echo "4️⃣ Comando em execução:"
kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].command}' | jq . 2>/dev/null || \
kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].command}'
echo ""

# 5. Verificar onde está o main.py
echo "5️⃣ Procurando main.py:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- find /app -name "main.py" -type f 2>/dev/null | head -5
echo ""

echo "=========================================="
echo "✅ Diagnóstico completo"
echo "=========================================="




