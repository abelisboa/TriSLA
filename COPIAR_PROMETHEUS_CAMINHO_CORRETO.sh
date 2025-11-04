#!/bin/bash
# Copiar prometheus.py para o local correto (/app/)

set -e

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

echo "=========================================="
echo "🚀 Copiando prometheus.py para /app/"
echo "=========================================="
echo "Pod: $POD_NAME | Container: $CONTAINER"
echo ""

# Verificar arquivo local
if [ ! -f "apps/api/prometheus.py" ]; then
    echo "❌ Arquivo apps/api/prometheus.py não encontrado localmente!"
    exit 1
fi

# Copiar usando base64
echo "📦 Codificando e copiando..."
PROM_B64=$(cat apps/api/prometheus.py | base64 -w 0)

cat > /tmp/copy_prom.py << 'PYEOF'
import sys
import base64
b64_data = sys.stdin.read().strip()
content = base64.b64decode(b64_data).decode('utf-8')
with open('/app/prometheus.py', 'w') as f:
    f.write(content)
print(f"✅ Criado /app/prometheus.py: {len(content)} bytes, {len(content.splitlines())} linhas")
PYEOF

kubectl cp /tmp/copy_prom.py trisla/$POD_NAME:/tmp/copy_prom.py -c $CONTAINER
echo "$PROM_B64" | kubectl exec -i -n trisla $POD_NAME -c $CONTAINER -- python3 /tmp/copy_prom.py

# Verificar
echo ""
echo "🔍 Verificando..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/prometheus.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- head -5 /app/prometheus.py

# Limpar
rm /tmp/copy_prom.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- rm /tmp/copy_prom.py 2>/dev/null

echo ""
echo "✅ Processo completo!"




