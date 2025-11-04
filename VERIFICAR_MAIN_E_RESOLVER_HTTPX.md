# ✅ Verificar main.py e Resolver httpx

## ✅ Status Atual

- ✅ `prometheus.py` copiado para `/app/prometheus.py` (4352 bytes, 119 linhas)
- ❌ `httpx` não está disponível
- ⚠️ Router pode não estar no `main.py` do pod

---

## 🔍 PASSO 1: Verificar main.py do Pod

```bash
cd ~/gtp5g/trisla-portal

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

# Ver todo o final do main.py
echo "Final do main.py (últimas 30 linhas):"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- tail -30 /app/main.py

# Procurar por prometheus
echo ""
echo "Procurando 'prometheus' no main.py:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- grep -i "prometheus" /app/main.py || echo "Não encontrado"
```

---

## 🔧 PASSO 2: Copiar main.py Atualizado (Se Necessário)

Se o router não estiver no main.py do pod:

```bash
# Copiar main.py atualizado
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
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- rm /tmp/copy_main.py 2>/dev/null
```

---

## ⚠️ PASSO 3: Resolver httpx

### Opção A: Tentar Instalar httpx Manualmente (Pode Falhar)

```bash
# Tentar baixar e instalar httpx manualmente (se tiver acesso a arquivos locais)
# OU usar uma versão offline do httpx

# Verificar se há alguma forma de instalar offline
echo "Verificando se há pip cache ou outro método..."
```

### Opção B: Modificar prometheus.py para Usar requests (Se Disponível)

Se `requests` estiver disponível (é mais comum), podemos modificar temporariamente:

```bash
# Verificar se requests está disponível
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 -c "import requests; print('✅ requests OK')" 2>&1
```

### Opção C: Rebuild Imagem (Recomendado)

```bash
# 1. Garantir que httpx está no requirements.txt
grep -q "httpx" apps/api/requirements.txt || echo "httpx" >> apps/api/requirements.txt

# 2. Se tiver acesso ao Docker no node1:
cd apps/api
docker build -t ghcr.io/abelisboa/trisla-api:prometheus .
docker push ghcr.io/abelisboa/trisla-api:prometheus

# 3. Atualizar deployment
kubectl set image deployment/trisla-portal -n trisla \
  trisla-api=ghcr.io/abelisboa/trisla-api:prometheus

# 4. Aguardar rollout
kubectl rollout status deployment/trisla-portal -n trisla --timeout=5m
```

---

## 🎯 PASSO 4: Testar Router (Mesmo Sem httpx)

Podemos testar se o router é carregado, mesmo que dê erro ao chamar Prometheus:

```bash
# Reiniciar deployment
DEPLOY=$(kubectl get deployment -n trisla | grep portal | awk '{print $1}')
kubectl rollout restart deployment/$DEPLOY -n trisla
kubectl rollout status deployment/$DEPLOY -n trisla --timeout=5m

# Aguardar
sleep 15

# Testar endpoint (pode dar erro 500 se httpx não estiver, mas 404 significa router não carregado)
kubectl port-forward -n trisla svc/trisla-portal 8000:8000 > /tmp/pf.log 2>&1 &
sleep 5

curl -s http://localhost:8000/prometheus/health

# Ver logs
kubectl logs -n trisla $POD_NAME -c $CONTAINER --tail=50 | grep -i -E "prometheus|router|error|httpx"
```

---

## 📋 Comandos Completos (Execute no node1)

```bash
cd ~/gtp5g/trisla-portal

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

# 1. Verificar main.py
echo "1️⃣ Verificando main.py..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- tail -20 /app/main.py | grep -A 10 "prometheus" || \
  echo "⚠️ Router não encontrado no main.py"

# 2. Verificar se requests está disponível (alternativa a httpx)
echo ""
echo "2️⃣ Verificando requests..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 -c "import requests; print('✅ requests OK')" 2>&1

# 3. Se router não estiver, copiar main.py
if ! kubectl exec -n trisla $POD_NAME -c $CONTAINER -- grep -q "prometheus_router" /app/main.py 2>/dev/null; then
    echo ""
    echo "3️⃣ Router não encontrado - copiando main.py..."
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
    kubectl exec -n trisla $POD_NAME -c $CONTAINER -- rm /tmp/copy_main.py 2>/dev/null
fi

# 4. Reiniciar e testar
echo ""
echo "4️⃣ Reiniciando deployment..."
DEPLOY=$(kubectl get deployment -n trisla | grep portal | awk '{print $1}')
kubectl rollout restart deployment/$DEPLOY -n trisla
echo "Aguardando rollout..."
kubectl rollout status deployment/$DEPLOY -n trisla --timeout=5m
```




