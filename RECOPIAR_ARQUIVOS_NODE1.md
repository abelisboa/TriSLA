# 🔄 Recopiar Arquivos e Criar Solução Permanente

## ⚠️ Problema

Os arquivos foram perdidos no restart porque não estão na imagem Docker. Cada vez que o pod reinicia, volta para a imagem original.

---

## ✅ PASSO 1: Recopiar Arquivos (Temporário)

```bash
cd ~/gtp5g/trisla-portal

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

echo "Pod: $POD_NAME"
echo ""

# Copiar prometheus.py
echo "📦 Copiando prometheus.py..."
PROM_B64=$(cat apps/api/prometheus.py | base64 -w 0)
cat > /tmp/copy_prom.py << 'PYEOF'
import sys
import base64
b64_data = sys.stdin.read().strip()
content = base64.b64decode(b64_data).decode('utf-8')
with open('/app/prometheus.py', 'w') as f:
    f.write(content)
print(f"✅ prometheus.py criado: {len(content)} bytes")
PYEOF

kubectl cp /tmp/copy_prom.py trisla/$POD_NAME:/tmp/copy_prom.py -c $CONTAINER
echo "$PROM_B64" | kubectl exec -i -n trisla $POD_NAME -c $CONTAINER -- python3 /tmp/copy_prom.py
rm /tmp/copy_prom.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- rm /tmp/copy_prom.py 2>/dev/null
echo ""

# Copiar main.py
echo "📦 Copiando main.py..."
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
echo ""

# Verificar
echo "🔍 Verificando..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/prometheus.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- grep -q "prometheus_router" /app/main.py && \
  echo "✅ Router no main.py" || echo "❌ Router não no main.py"
```

---

## 🔄 PASSO 2: Reiniciar e Testar (SEM Reiniciar Deployment!)

Importante: NÃO reinicie o deployment, pois perderá os arquivos novamente! Apenas reinicie o uvicorn dentro do pod:

```bash
# NÃO FAÇA ISSO: kubectl rollout restart deployment/trisla-portal
# Isso reiniciará o pod e perderá os arquivos!

# Em vez disso, recarregar o código (se uvicorn suportar --reload)
# OU apenas testar se o endpoint funciona agora
```

Ou melhor ainda, usar um **init container** ou **configMap** para persistir os arquivos. Mas por enquanto, vamos testar:

```bash
# Testar endpoint
kubectl port-forward -n trisla svc/trisla-portal 8000:8000 > /tmp/pf.log 2>&1 &
sleep 5

curl -s http://localhost:8000/prometheus/health

# Ver logs
kubectl logs -n trisla $POD_NAME -c $CONTAINER --tail=30 | grep -i -E "prometheus|router"
```

---

## 🎯 PASSO 3: Solução Permanente (Usar ConfigMap)

Para persistir os arquivos, podemos usar ConfigMap:

```bash
# Criar ConfigMap com prometheus.py
kubectl create configmap prometheus-api --from-file=prometheus.py=apps/api/prometheus.py -n trisla --dry-run=client -o yaml | kubectl apply -f -

# Modificar deployment para montar ConfigMap
# Isso requer editar o Helm chart ou deployment diretamente
```

Ou melhor: **rebuildar a imagem Docker** com os arquivos incluídos.

---

## 📋 Comandos Completos (Recopiar e Testar)

```bash
cd ~/gtp5g/trisla-portal

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

# Copiar prometheus.py
PROM_B64=$(cat apps/api/prometheus.py | base64 -w 0)
cat > /tmp/copy_prom.py << 'PYEOF'
import sys, base64
b64_data = sys.stdin.read().strip()
content = base64.b64decode(b64_data).decode('utf-8')
with open('/app/prometheus.py', 'w') as f:
    f.write(content)
print(f"✅ prometheus.py: {len(content)} bytes")
PYEOF

kubectl cp /tmp/copy_prom.py trisla/$POD_NAME:/tmp/copy_prom.py -c $CONTAINER
echo "$PROM_B64" | kubectl exec -i -n trisla $POD_NAME -c $CONTAINER -- python3 /tmp/copy_prom.py
rm /tmp/copy_prom.py

# Copiar main.py
MAIN_B64=$(cat apps/api/main.py | base64 -w 0)
cat > /tmp/copy_main.py << 'PYEOF'
import sys, base64
b64_data = sys.stdin.read().strip()
content = base64.b64decode(b64_data).decode('utf-8')
with open('/app/main.py', 'w') as f:
    f.write(content)
print(f"✅ main.py: {len(content)} bytes")
PYEOF

kubectl cp /tmp/copy_main.py trisla/$POD_NAME:/tmp/copy_main.py -c $CONTAINER
echo "$MAIN_B64" | kubectl exec -i -n trisla $POD_NAME -c $CONTAINER -- python3 /tmp/copy_main.py
rm /tmp/copy_main.py

# Verificar
echo ""
echo "Verificando..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/prometheus.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- grep -q "prometheus_router" /app/main.py && echo "✅ Router OK" || echo "❌ Router faltando"

# Aguardar alguns segundos para API recarregar
sleep 5

# Testar
echo ""
echo "Testando endpoint..."
kubectl port-forward -n trisla svc/trisla-portal 8000:8000 > /tmp/pf.log 2>&1 &
sleep 5
curl -s http://localhost:8000/prometheus/health
echo ""
```




