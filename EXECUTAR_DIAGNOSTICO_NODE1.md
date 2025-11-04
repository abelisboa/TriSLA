# 🔍 Execute Diagnóstico no node1

## ✅ Execute Estes Comandos

```bash
cd ~/gtp5g/trisla-portal

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

echo "=========================================="
echo "🔍 Diagnóstico Router Prometheus"
echo "=========================================="
echo ""

# 1. Verificar arquivos
echo "1️⃣ Arquivos:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/apps/api/prometheus.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/apps/api/main.py
echo ""

# 2. Verificar httpx
echo "2️⃣ httpx:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 -c "import httpx; print('✅ httpx OK')" 2>&1
echo ""

# 3. Testar import
echo "3️⃣ Testando import prometheus:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 << 'PYEOF'
import sys
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/apps/api')

try:
    from prometheus import router
    print('✅ Import OK')
    print(f'Router prefix: {router.prefix}')
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
PYEOF
echo ""

# 4. Verificar main.py
echo "4️⃣ Router no main.py:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- grep -B 2 -A 5 "prometheus" /app/apps/api/main.py
echo ""

# 5. Ver logs
echo "5️⃣ Logs (prometheus/router):"
kubectl logs -n trisla $POD_NAME -c $CONTAINER --tail=200 | grep -i -E "prometheus|router.*prometheus" | tail -10
echo ""

# 6. Ver todos os logs de inicialização
echo "6️⃣ Logs completos (últimas 50 linhas):"
kubectl logs -n trisla $POD_NAME -c $CONTAINER --tail=50
```

---

## 🔧 Ou Execute o Script Automático

```bash
# Copiar script para node1 primeiro (ou criar diretamente)
cat > DIAGNOSTICAR_ROUTER_NODE1.sh << 'SCRIPTEOF'
#!/bin/bash
# [conteúdo do script]
SCRIPTEOF

chmod +x DIAGNOSTICAR_ROUTER_NODE1.sh
./DIAGNOSTICAR_ROUTER_NODE1.sh
```




