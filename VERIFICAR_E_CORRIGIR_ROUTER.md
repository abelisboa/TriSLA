# 🔧 Verificar e Corrigir Router Prometheus

## ❌ Problema Detectado

- Endpoint `/prometheus/health` retorna **404 Not Found**
- Router não está sendo carregado

---

## ✅ Diagnóstico e Correção

### PASSO 1: Verificar se httpx está disponível

```bash
POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

# Testar httpx (comando simples)
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 -c "import httpx; print('OK')" 2>&1
```

---

### PASSO 2: Verificar main.py no pod

```bash
# Ver se router está no main.py
echo "Verificando main.py..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- grep -A 5 "prometheus_router" /app/apps/api/main.py

# Ver se prometheus.py existe
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/apps/api/prometheus.py

# Testar import do prometheus
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 -c "
import sys
sys.path.insert(0, '/app/apps/api')
try:
    from prometheus import router
    print('✅ Import OK')
except Exception as e:
    print(f'❌ Erro: {e}')
"
```

---

### PASSO 3: Ver logs completos para erros

```bash
# Ver logs com mais detalhes
kubectl logs -n trisla -l app=trisla-portal --tail=100 -c $CONTAINER | grep -i -E "prometheus|error|traceback|exception" || \
kubectl logs -n trisla -l app=trisla-portal --tail=100 -c $CONTAINER
```

---

### PASSO 4: Verificar estrutura do código

O problema pode ser:
1. `prometheus.py` não está no caminho correto
2. `main.py` não está importando corretamente
3. Erro de sintaxe no `prometheus.py`
4. `httpx` não está disponível

```bash
# Verificar estrutura
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- find /app -name "*.py" -path "*/api/*" | head -10

# Verificar PYTHONPATH
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- env | grep PYTHONPATH

# Ver como main.py está tentando importar
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- grep -B 2 -A 10 "from prometheus" /app/apps/api/main.py || \
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- grep -B 2 -A 10 "prometheus_router" /app/apps/api/main.py
```

---

## 🔧 Possíveis Correções

### Correção 1: Verificar caminho de import

Se o código está em `/app/apps/api/`, o import pode precisar ser diferente:

```bash
# Ver como está o import no main.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- cat /app/apps/api/main.py | grep -A 5 "prometheus"
```

O import correto pode ser:
- `from apps.api.prometheus import router` (se PYTHONPATH inclui /app)
- `from prometheus import router` (se PYTHONPATH inclui /app/apps/api)

### Correção 2: Recopiar main.py com import correto

```bash
# Verificar main.py local primeiro
grep -A 5 "prometheus" apps/api/main.py

# Se necessário, ajustar e copiar novamente
```

---

## 📋 Comandos Completos de Diagnóstico

```bash
cd ~/gtp5g/trisla-portal

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

echo "=========================================="
echo "🔍 Diagnóstico Completo"
echo "=========================================="
echo ""

# 1. Verificar arquivos
echo "1️⃣ Arquivos:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/apps/api/*.py | head -5
echo ""

# 2. Verificar httpx
echo "2️⃣ httpx:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 -c "import httpx; print('✅ httpx OK')" 2>&1
echo ""

# 3. Verificar import
echo "3️⃣ Import prometheus:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 << 'PYEOF'
import sys
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/apps/api')
try:
    from prometheus import router
    print('✅ Import prometheus OK')
except Exception as e:
    print(f'❌ Erro import: {e}')
    import traceback
    traceback.print_exc()
PYEOF
echo ""

# 4. Verificar main.py
echo "4️⃣ Router no main.py:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- grep -B 3 -A 5 "prometheus" /app/apps/api/main.py
echo ""

# 5. Ver logs de inicialização
echo "5️⃣ Logs de inicialização:"
kubectl logs -n trisla $POD_NAME -c $CONTAINER --tail=50 | grep -i -E "prometheus|router|started|uvicorn" | tail -10
echo ""
```




