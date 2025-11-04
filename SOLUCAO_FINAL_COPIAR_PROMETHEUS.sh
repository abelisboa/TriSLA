#!/bin/bash
# Solução final para copiar prometheus.py - Usa Python dentro do pod

set -e

echo "=========================================="
echo "🚀 Copiando prometheus.py para Pod"
echo "=========================================="

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

echo "Pod: $POD_NAME"
echo "Container: $CONTAINER"
echo ""

# Ler arquivo local e criar no pod usando Python
echo "📦 Copiando arquivo..."

cat apps/api/prometheus.py | kubectl exec -i -n trisla $POD_NAME -c $CONTAINER -- python3 << 'PYEOF'
import sys
import os

# Criar diretório
os.makedirs('/app/apps/api', exist_ok=True)

# Ler conteúdo de stdin
content = sys.stdin.read()

# Escrever arquivo
with open('/app/apps/api/prometheus.py', 'w') as f:
    f.write(content)

print(f"✅ Arquivo criado em /app/apps/api/prometheus.py ({len(content)} bytes)")
PYEOF

if [ $? -eq 0 ]; then
    echo "✅ Sucesso!"
else
    echo "❌ Erro ao copiar"
    exit 1
fi

# Verificar
echo ""
echo "🔍 Verificando..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/apps/api/prometheus.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- head -3 /app/apps/api/prometheus.py

echo ""
echo "=========================================="
echo "✅ Processo completo!"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "1. Verificar se httpx está instalado"
echo "2. Atualizar main.py se necessário"
echo "3. Reiniciar deployment"
echo ""




