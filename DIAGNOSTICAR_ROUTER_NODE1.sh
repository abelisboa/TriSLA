#!/bin/bash
# Diagnóstico completo do router Prometheus

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

echo "=========================================="
echo "🔍 Diagnóstico Router Prometheus"
echo "=========================================="
echo "Pod: $POD_NAME | Container: $CONTAINER"
echo ""

# 1. Verificar arquivos
echo "1️⃣ Arquivos:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/apps/api/prometheus.py 2>/dev/null || echo "❌ prometheus.py não encontrado"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/apps/api/main.py 2>/dev/null || echo "❌ main.py não encontrado"
echo ""

# 2. Verificar httpx
echo "2️⃣ httpx:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 -c "import httpx; print('✅ httpx disponível')" 2>&1
echo ""

# 3. Verificar import prometheus
echo "3️⃣ Testando import prometheus:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 << 'PYEOF'
import sys
import os

# Tentar diferentes caminhos
paths = ['/app', '/app/apps', '/app/apps/api']
for p in paths:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from prometheus import router
    print('✅ Import OK')
    print(f'Router prefix: {router.prefix}')
except Exception as e:
    print(f'❌ Erro import: {e}')
    import traceback
    traceback.print_exc()
PYEOF
echo ""

# 4. Verificar main.py
echo "4️⃣ Router no main.py:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- grep -B 2 -A 5 "prometheus" /app/apps/api/main.py | head -10
echo ""

# 5. Ver logs de inicialização (última vez que iniciou)
echo "5️⃣ Logs de inicialização:"
kubectl logs -n trisla $POD_NAME -c $CONTAINER --tail=200 | grep -i -E "prometheus|router|started|uvicorn" | tail -15
echo ""

# 6. Verificar se há erros recentes
echo "6️⃣ Erros recentes:"
kubectl logs -n trisla $POD_NAME -c $CONTAINER --tail=50 | grep -i -E "error|exception|traceback|warning.*prometheus" || echo "Nenhum erro específico encontrado"
echo ""

echo "=========================================="
echo "✅ Diagnóstico completo"
echo "=========================================="




