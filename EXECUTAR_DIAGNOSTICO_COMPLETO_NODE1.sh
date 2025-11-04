#!/bin/bash
# Diagnóstico completo do problema do router

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

echo "=========================================="
echo "🔍 Diagnóstico Completo Router Prometheus"
echo "=========================================="
echo "Pod: $POD_NAME"
echo ""

# 1. Verificar arquivos
echo "1️⃣ Arquivos:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/prometheus.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- grep -q "prometheus_router" /app/main.py && \
  echo "✅ Router no main.py" || echo "❌ Router não no main.py"
echo ""

# 2. Verificar httpx
echo "2️⃣ httpx:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 -c "import httpx; print('✅ httpx OK')" 2>&1
echo ""

# 3. Testar import prometheus
echo "3️⃣ Testando import prometheus:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 << 'PYEOF'
import sys
sys.path.insert(0, '/app')
print("Tentando importar prometheus...")
try:
    from prometheus import router
    print('✅ Import OK')
    print(f'Router prefix: {router.prefix}')
    print(f'Rotas: {len(router.routes)}')
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
PYEOF
echo ""

# 4. Ver logs
echo "4️⃣ Logs (prometheus/router/error):"
kubectl logs -n trisla $POD_NAME -c $CONTAINER --tail=200 | grep -i -E "prometheus|router.*prometheus|warning.*prometheus" | tail -15
echo ""

# 5. Ver logs completos recentes
echo "5️⃣ Logs completos (últimas 20 linhas):"
kubectl logs -n trisla $POD_NAME -c $CONTAINER --tail=20
echo ""

echo "=========================================="
echo "✅ Diagnóstico completo"
echo "=========================================="




