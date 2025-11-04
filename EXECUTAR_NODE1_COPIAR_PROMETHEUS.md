# ✅ Execute Estes Comandos no node1

## 🎯 Solução Mais Simples (Execute Tudo)

```bash
cd ~/gtp5g/trisla-portal

# 1. Identificar pod
POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')
echo "Pod: $POD_NAME | Container: $CONTAINER"

# 2. Copiar prometheus.py usando Python (mais confiável)
cat apps/api/prometheus.py | kubectl exec -i -n trisla $POD_NAME -c $CONTAINER -- python3 << 'PYEOF'
import sys
import os
os.makedirs('/app/apps/api', exist_ok=True)
content = sys.stdin.read()
with open('/app/apps/api/prometheus.py', 'w') as f:
    f.write(content)
print(f"✅ Arquivo criado: {len(content)} bytes")
PYEOF

# 3. Verificar
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/apps/api/prometheus.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- head -5 /app/apps/api/prometheus.py

# 4. Verificar httpx
echo "Verificando httpx..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- pip list | grep httpx || echo "⚠️ httpx não instalado"

# 5. Verificar main.py
echo "Verificando main.py..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- grep -q "prometheus_router" /app/apps/api/main.py 2>/dev/null && \
  echo "✅ Router já está no main.py" || \
  echo "⚠️ Router não encontrado - precisa adicionar"
```

---

## 🔧 Se httpx não estiver instalado

```bash
# Tentar instalar (pode falhar por rede)
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- pip install httpx

# OU adicionar ao requirements.txt local e rebuild imagem
echo "httpx" >> apps/api/requirements.txt
```

---

## 📝 Se main.py não tiver o router

```bash
# Copiar main.py também (se modificado localmente)
cat apps/api/main.py | kubectl exec -i -n trisla $POD_NAME -c $CONTAINER -- python3 << 'PYEOF'
import sys
content = sys.stdin.read()
with open('/app/apps/api/main.py', 'w') as f:
    f.write(content)
print("✅ main.py atualizado")
PYEOF
```

---

## 🔄 Reiniciar Deployment

```bash
# Encontrar deployment
DEPLOY=$(kubectl get deployment -n trisla | grep portal | awk '{print $1}')

# Reiniciar
kubectl rollout restart deployment/$DEPLOY -n trisla

# Aguardar
kubectl rollout status deployment/$DEPLOY -n trisla --timeout=5m

# Testar
sleep 10
curl http://localhost:8092/prometheus/health
```

---

## 🚀 OU Execute o Script Automático

```bash
chmod +x SOLUCAO_FINAL_COPIAR_PROMETHEUS.sh
./SOLUCAO_FINAL_COPIAR_PROMETHEUS.sh
```




