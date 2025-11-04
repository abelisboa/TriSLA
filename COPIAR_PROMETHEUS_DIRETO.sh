#!/bin/bash
# Método direto - criar script Python temporário

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

echo "Pod: $POD_NAME | Container: $CONTAINER"
echo ""

# Criar script Python temporário
cat > /tmp/copy_prometheus.py << 'PYSCRIPT'
import sys
import os

# Ler base64 de stdin
b64_data = sys.stdin.read().strip()
content = __import__('base64').b64decode(b64_data).decode('utf-8')

# Criar diretório
os.makedirs('/app/apps/api', exist_ok=True)

# Escrever arquivo
with open('/app/apps/api/prometheus.py', 'w') as f:
    f.write(content)

print(f"✅ Arquivo criado: {len(content)} bytes, {len(content.splitlines())} linhas")
PYSCRIPT

# Codificar arquivo
echo "📦 Codificando..."
BASE64_DATA=$(base64 -w 0 apps/api/prometheus.py)

# Copiar script para pod
kubectl cp /tmp/copy_prometheus.py trisla/$POD_NAME:/tmp/copy_prometheus.py -c $CONTAINER

# Executar script no pod
echo "$BASE64_DATA" | kubectl exec -i -n trisla $POD_NAME -c $CONTAINER -- python3 /tmp/copy_prometheus.py

# Verificar
echo ""
echo "🔍 Verificando..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/apps/api/prometheus.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- wc -l /app/apps/api/prometheus.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- head -10 /app/apps/api/prometheus.py

# Limpar
rm /tmp/copy_prometheus.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- rm /tmp/copy_prometheus.py

echo ""
echo "✅ Processo completo!"




