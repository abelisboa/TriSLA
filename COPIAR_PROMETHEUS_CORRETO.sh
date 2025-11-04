#!/bin/bash
# Método correto usando base64

set -e

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

echo "Pod: $POD_NAME | Container: $CONTAINER"
echo ""

# Verificar se arquivo local existe
if [ ! -f "apps/api/prometheus.py" ]; then
    echo "❌ Arquivo apps/api/prometheus.py não encontrado!"
    exit 1
fi

# Ler arquivo e codificar em base64
echo "📦 Codificando arquivo..."
BASE64_DATA=$(base64 -w 0 apps/api/prometheus.py)

# Criar no pod usando base64
echo "📤 Copiando para o pod..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 << PYEOF
import base64
import os

# Criar diretório
os.makedirs('/app/apps/api', exist_ok=True)

# Decodificar base64
b64_data = '''$BASE64_DATA'''
content = base64.b64decode(b64_data).decode('utf-8')

# Escrever arquivo
with open('/app/apps/api/prometheus.py', 'w') as f:
    f.write(content)

print(f"✅ Arquivo criado: {len(content)} bytes")
PYEOF

# Verificar
echo ""
echo "🔍 Verificando..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/apps/api/prometheus.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- wc -l /app/apps/api/prometheus.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- head -10 /app/apps/api/prometheus.py

echo ""
echo "✅ Processo completo!"




