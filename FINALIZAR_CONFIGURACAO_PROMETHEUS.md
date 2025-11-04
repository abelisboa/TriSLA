# ✅ Finalizar Configuração do Prometheus API

## ✅ Arquivo Criado com Sucesso!

- ✅ `prometheus.py` criado: 4352 bytes, 119 linhas
- 📍 Localização: `/app/apps/api/prometheus.py` no pod

---

## 🔧 Próximos Passos

### PASSO 1: Verificar httpx

```bash
POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

echo "Verificando httpx..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- pip list | grep httpx
```

Se não estiver instalado:
```bash
# Tentar instalar (pode falhar por rede)
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- pip install httpx

# OU adicionar ao requirements.txt e rebuild imagem (recomendado)
echo "httpx" >> apps/api/requirements.txt
```

---

### PASSO 2: Verificar/Copiar main.py

```bash
# Verificar se router já está no main.py do pod
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- grep -q "prometheus_router" /app/apps/api/main.py && \
  echo "✅ Router já está no main.py" || \
  echo "⚠️ Router não encontrado"

# Se não estiver, copiar main.py também
if ! kubectl exec -n trisla $POD_NAME -c $CONTAINER -- grep -q "prometheus_router" /app/apps/api/main.py 2>/dev/null; then
    echo "Copiando main.py..."
    
    # Usar mesmo método (base64)
    MAIN_FILE=$(cat apps/api/main.py)
    MAIN_B64=$(echo "$MAIN_FILE" | base64 -w 0)
    
    cat > /tmp/copy_main.py << 'PYEOF'
    import sys
    import base64
    b64_data = sys.stdin.read().strip()
    content = base64.b64decode(b64_data).decode('utf-8')
    with open('/app/apps/api/main.py', 'w') as f:
        f.write(content)
    print(f"✅ main.py atualizado: {len(content)} bytes")
PYEOF
    
    kubectl cp /tmp/copy_main.py trisla/$POD_NAME:/tmp/copy_main.py -c $CONTAINER
    echo "$MAIN_B64" | kubectl exec -i -n trisla $POD_NAME -c $CONTAINER -- python3 /tmp/copy_main.py
    rm /tmp/copy_main.py
    kubectl exec -n trisla $POD_NAME -c $CONTAINER -- rm /tmp/copy_main.py
fi
```

---

### PASSO 3: Reiniciar Deployment

```bash
# Encontrar deployment
DEPLOY=$(kubectl get deployment -n trisla | grep portal | awk '{print $1}')
echo "Deployment: $DEPLOY"

# Reiniciar
kubectl rollout restart deployment/$DEPLOY -n trisla

# Aguardar rollout
echo "Aguardando rollout..."
kubectl rollout status deployment/$DEPLOY -n trisla --timeout=5m
```

---

### PASSO 4: Verificar Logs

```bash
# Aguardar alguns segundos
sleep 10

# Ver logs
kubectl logs -n trisla -l app=trisla-portal --tail=50 -c $CONTAINER | grep -i prometheus || \
kubectl logs -n trisla -l app=trisla-portal --tail=50 | grep -i prometheus || \
kubectl logs -n trisla -l app=trisla-portal --tail=50
```

---

### PASSO 5: Testar Endpoint

```bash
# Aguardar API iniciar
sleep 15

# Testar via port-forward existente (porta 8092)
echo "Testando http://localhost:8092/prometheus/health..."
curl -s http://localhost:8092/prometheus/health | jq . || curl -s http://localhost:8092/prometheus/health

# Se não funcionar, criar novo port-forward
echo ""
echo "Se não funcionar, criar novo port-forward:"
echo "kubectl port-forward -n trisla svc/trisla-portal 8000:8000 &"
echo "sleep 3"
echo "curl http://localhost:8000/prometheus/health"
```

---

## 🎯 Script Completo (Execute Tudo de Uma Vez)

```bash
cd ~/gtp5g/trisla-portal

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

echo "=========================================="
echo "🔧 Finalizando Configuração Prometheus"
echo "=========================================="
echo "Pod: $POD_NAME | Container: $CONTAINER"
echo ""

# 1. Verificar httpx
echo "1️⃣ Verificando httpx..."
if kubectl exec -n trisla $POD_NAME -c $CONTAINER -- pip list 2>/dev/null | grep -q httpx; then
    echo "✅ httpx já instalado"
else
    echo "⚠️ httpx não encontrado"
    kubectl exec -n trisla $POD_NAME -c $CONTAINER -- pip install httpx 2>/dev/null && \
      echo "✅ httpx instalado" || \
      echo "⚠️ Não foi possível instalar httpx (problema de rede)"
fi
echo ""

# 2. Verificar main.py
echo "2️⃣ Verificando main.py..."
if kubectl exec -n trisla $POD_NAME -c $CONTAINER -- grep -q "prometheus_router" /app/apps/api/main.py 2>/dev/null; then
    echo "✅ Router já está no main.py"
else
    echo "⚠️ Router não encontrado - copiando main.py..."
    
    MAIN_B64=$(cat apps/api/main.py | base64 -w 0)
    cat > /tmp/copy_main.py << 'PYEOF'
import sys
import base64
b64_data = sys.stdin.read().strip()
content = base64.b64decode(b64_data).decode('utf-8')
with open('/app/apps/api/main.py', 'w') as f:
    f.write(content)
print(f"✅ main.py atualizado: {len(content)} bytes")
PYEOF
    
    kubectl cp /tmp/copy_main.py trisla/$POD_NAME:/tmp/copy_main.py -c $CONTAINER
    echo "$MAIN_B64" | kubectl exec -i -n trisla $POD_NAME -c $CONTAINER -- python3 /tmp/copy_main.py
    rm /tmp/copy_main.py
    kubectl exec -n trisla $POD_NAME -c $CONTAINER -- rm /tmp/copy_main.py 2>/dev/null
fi
echo ""

# 3. Reiniciar deployment
echo "3️⃣ Reiniciando deployment..."
DEPLOY=$(kubectl get deployment -n trisla | grep portal | awk '{print $1}')
kubectl rollout restart deployment/$DEPLOY -n trisla
kubectl rollout status deployment/$DEPLOY -n trisla --timeout=5m
echo ""

# 4. Aguardar e testar
echo "4️⃣ Aguardando API iniciar..."
sleep 15

echo "5️⃣ Testando endpoint..."
curl -s http://localhost:8092/prometheus/health || \
  echo "⚠️ Endpoint não acessível. Criar port-forward:"
  echo "   kubectl port-forward -n trisla svc/trisla-portal 8000:8000"

echo ""
echo "=========================================="
echo "✅ Processo completo!"
echo "=========================================="
```




