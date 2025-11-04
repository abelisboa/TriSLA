#!/bin/bash
# Descobrir estrutura real do pod

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

echo "=========================================="
echo "🔍 Descobrindo Estrutura Real do Pod"
echo "=========================================="
echo "Pod: $POD_NAME | Container: $CONTAINER"
echo ""

# 1. Ver estrutura /app
echo "1️⃣ Estrutura /app:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -la /app | head -20
echo ""

# 2. Procurar main.py
echo "2️⃣ Procurando main.py:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- find /app -name "main.py" -type f 2>/dev/null
echo ""

# 3. Ver comando que está rodando
echo "3️⃣ Comando rodando:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ps aux | grep uvicorn | grep -v grep
echo ""

# 4. Ver PYTHONPATH
echo "4️⃣ PYTHONPATH:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- env | grep PYTHONPATH
echo ""

# 5. Verificar onde prometheus.py foi criado
echo "5️⃣ Procurando prometheus.py:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- find /app -name "prometheus.py" -type f 2>/dev/null
echo ""

echo "=========================================="
echo "✅ Diagnóstico completo"
echo "=========================================="




