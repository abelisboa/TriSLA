# ✅ Comandos Finais para Copiar prometheus.py

## 🎯 Método Mais Confiável (Execute no node1)

```bash
cd ~/gtp5g/trisla-portal

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

echo "Pod: $POD_NAME | Container: $CONTAINER"

# Criar script Python temporário local
cat > /tmp/copy_prom.py << 'PYEOF'
import sys
import base64
import os

b64_data = sys.stdin.read().strip()
content = base64.b64decode(b64_data).decode('utf-8')

os.makedirs('/app/apps/api', exist_ok=True)

with open('/app/apps/api/prometheus.py', 'w') as f:
    f.write(content)

print(f"✅ Criado: {len(content)} bytes, {content.count(chr(10))} linhas")
PYEOF

# Codificar arquivo
BASE64_DATA=$(base64 -w 0 apps/api/prometheus.py)

# Copiar script para pod
kubectl cp /tmp/copy_prom.py trisla/$POD_NAME:/tmp/copy_prom.py -c $CONTAINER

# Executar: passar base64 via stdin
echo "$BASE64_DATA" | kubectl exec -i -n trisla $POD_NAME -c $CONTAINER -- python3 /tmp/copy_prom.py

# Verificar
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- wc -l /app/apps/api/prometheus.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- head -10 /app/apps/api/prometheus.py

# Limpar
rm /tmp/copy_prom.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- rm /tmp/copy_prom.py
```

---

## 🔧 Método Alternativo: Linha por Linha

Se base64 não funcionar, usar este método (mais lento mas funciona sempre):

```bash
POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

# Criar arquivo vazio
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- bash -c "mkdir -p /app/apps/api && touch /app/apps/api/prometheus.py"

# Adicionar linha por linha (método confiável mas lento)
while IFS= read -r line; do
    # Escapar caracteres especiais
    escaped=$(printf '%s\n' "$line" | sed "s/'/'\\\\''/g")
    kubectl exec -n trisla $POD_NAME -c $CONTAINER -- bash -c "echo '$escaped' >> /app/apps/api/prometheus.py"
done < apps/api/prometheus.py

# Verificar
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- wc -l /app/apps/api/prometheus.py
```

---

## 🚀 Método Mais Rápido: Arquivo Completo em uma Variável

```bash
POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

# Ler arquivo completo
PROM_FILE=$(cat apps/api/prometheus.py)

# Criar no pod usando printf (mais confiável que echo)
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 << EOF
import os
content = '''$PROM_FILE'''
os.makedirs('/app/apps/api', exist_ok=True)
with open('/app/apps/api/prometheus.py', 'w') as f:
    f.write(content)
print(f"✅ Criado: {len(content)} bytes")
EOF

# Verificar
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- wc -l /app/apps/api/prometheus.py
```

---

## ✅ Após Copiar com Sucesso

```bash
# 1. Verificar httpx
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- pip list | grep httpx || \
  echo "⚠️ Precisa instalar httpx"

# 2. Verificar main.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- grep "prometheus_router" /app/apps/api/main.py || \
  echo "⚠️ Precisa adicionar router no main.py"

# 3. Reiniciar deployment
DEPLOY=$(kubectl get deployment -n trisla | grep portal | awk '{print $1}')
kubectl rollout restart deployment/$DEPLOY -n trisla
kubectl rollout status deployment/$DEPLOY -n trisla --timeout=5m

# 4. Testar
sleep 15
curl http://localhost:8092/prometheus/health
```




