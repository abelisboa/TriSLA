# ✅ Copiar prometheus.py para /app/ (Caminho Correto)

## ✅ Estrutura Descoberta

- ✅ `main.py` está em `/app/main.py`
- ✅ `PYTHONPATH=/app:/app/apps/api`
- ❌ `prometheus.py` não existe (foi copiado para local errado)

---

## 🎯 Execute Estes Comandos no node1

```bash
cd ~/gtp5g/trisla-portal

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

echo "📦 Copiando prometheus.py para /app/..."

# Codificar arquivo
PROM_B64=$(cat apps/api/prometheus.py | base64 -w 0)

# Criar script Python
cat > /tmp/copy_prom.py << 'PYEOF'
import sys
import base64
b64_data = sys.stdin.read().strip()
content = base64.b64decode(b64_data).decode('utf-8')
with open('/app/prometheus.py', 'w') as f:
    f.write(content)
print(f"✅ Criado /app/prometheus.py: {len(content)} bytes, {len(content.splitlines())} linhas")
PYEOF

# Copiar script e executar
kubectl cp /tmp/copy_prom.py trisla/$POD_NAME:/tmp/copy_prom.py -c $CONTAINER
echo "$PROM_B64" | kubectl exec -i -n trisla $POD_NAME -c $CONTAINER -- python3 /tmp/copy_prom.py

# Verificar
echo ""
echo "🔍 Verificando..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/prometheus.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- wc -l /app/prometheus.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- head -5 /app/prometheus.py

# Limpar
rm /tmp/copy_prom.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- rm /tmp/copy_prom.py 2>/dev/null
```

---

## 🔍 Verificar main.py no Pod

```bash
# Verificar se router está no main.py do pod
echo "Verificando router no main.py..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- grep -A 5 "prometheus" /app/main.py | head -10
```

Se não estiver, copiar main.py também:

```bash
# Copiar main.py
MAIN_B64=$(cat apps/api/main.py | base64 -w 0)
cat > /tmp/copy_main.py << 'PYEOF'
import sys
import base64
b64_data = sys.stdin.read().strip()
content = base64.b64decode(b64_data).decode('utf-8')
with open('/app/main.py', 'w') as f:
    f.write(content)
print(f"✅ main.py atualizado: {len(content)} bytes")
PYEOF

kubectl cp /tmp/copy_main.py trisla/$POD_NAME:/tmp/copy_main.py -c $CONTAINER
echo "$MAIN_B64" | kubectl exec -i -n trisla $POD_NAME -c $CONTAINER -- python3 /tmp/copy_main.py
rm /tmp/copy_main.py
```

---

## 🧪 Testar Import e httpx

```bash
# Testar httpx
echo "Testando httpx..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 -c "import httpx; print('✅ httpx OK')" 2>&1

# Testar import prometheus
echo ""
echo "Testando import prometheus..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 << 'PYEOF'
import sys
sys.path.insert(0, '/app')
try:
    from prometheus import router
    print('✅ Import prometheus OK')
    print(f'Router prefix: {router.prefix}')
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
PYEOF
```

---

## 🔄 Reiniciar Deployment

```bash
# Reiniciar
DEPLOY=$(kubectl get deployment -n trisla | grep portal | awk '{print $1}')
kubectl rollout restart deployment/$DEPLOY -n trisla
kubectl rollout status deployment/$DEPLOY -n trisla --timeout=5m

# Testar endpoint
sleep 15
kubectl port-forward -n trisla svc/trisla-portal 8000:8000 > /tmp/pf.log 2>&1 &
sleep 5
curl -s http://localhost:8000/prometheus/health | jq . || curl -s http://localhost:8000/prometheus/health
```




