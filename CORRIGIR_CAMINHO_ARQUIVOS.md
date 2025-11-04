# 🔧 Corrigir Caminho dos Arquivos

## ❌ Problema Detectado

Os arquivos **NÃO estão** em `/app/apps/api/`! Precisamos descobrir onde estão realmente.

---

## ✅ Execute Primeiro para Descobrir Estrutura

```bash
cd ~/gtp5g/trisla-portal

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

echo "1️⃣ Estrutura /app:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -la /app | head -20
echo ""

echo "2️⃣ Procurando main.py:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- find /app -name "main.py" -type f 2>/dev/null
echo ""

echo "3️⃣ Procurando prometheus.py:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- find /app -name "prometheus.py" -type f 2>/dev/null
echo ""

echo "4️⃣ Comando rodando:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ps aux | grep uvicorn | grep -v grep
echo ""

echo "5️⃣ PYTHONPATH:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- env | grep -E "PYTHONPATH|PWD"
```

---

## 📋 Possíveis Estruturas

Baseado no Dockerfile (`WORKDIR /app` e `CMD ["uvicorn", "main:app"]`), os arquivos provavelmente estão:

### Opção 1: `/app/` (raiz)
- `/app/main.py`
- `/app/prometheus.py` (criar aqui)

### Opção 2: `/app/api/`
- `/app/api/main.py`
- `/app/api/prometheus.py`

### Opção 3: `/app/apps/api/` (o que tentamos, mas não existe)

---

## 🔧 Após Descobrir, Copiar para Local Correto

Depois de descobrir onde está `main.py`, copiar `prometheus.py` para o mesmo diretório:

```bash
# Exemplo: Se main.py estiver em /app/
PROM_B64=$(cat apps/api/prometheus.py | base64 -w 0)
cat > /tmp/copy_prom.py << 'PYEOF'
import sys
import base64
b64_data = sys.stdin.read().strip()
content = base64.b64decode(b64_data).decode('utf-8')
with open('/app/prometheus.py', 'w') as f:  # AJUSTAR CAMINHO AQUI
    f.write(content)
print(f"✅ Criado: {len(content)} bytes")
PYEOF

kubectl cp /tmp/copy_prom.py trisla/$POD_NAME:/tmp/copy_prom.py -c $CONTAINER
echo "$PROM_B64" | kubectl exec -i -n trisla $POD_NAME -c $CONTAINER -- python3 /tmp/copy_prom.py
```

---

## 🔄 Ajustar main.py também

Se o `main.py` estiver em outro local, precisamos verificar o import:

- Se estiver em `/app/` → `from prometheus import router`
- Se estiver em `/app/api/` → pode precisar ajustar PYTHONPATH ou import

Execute os comandos de diagnóstico primeiro!




