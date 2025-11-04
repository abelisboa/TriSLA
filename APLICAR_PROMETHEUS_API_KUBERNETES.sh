#!/bin/bash
# Script para aplicar prometheus.py no Kubernetes

echo "=========================================="
echo "🚀 Aplicando Prometheus API no Kubernetes"
echo "=========================================="
echo ""

# 1. Verificar pods
echo "1️⃣ Verificando pods..."
kubectl get pods -n trisla | grep portal
POD_NAME=$(kubectl get pods -n trisla -l app=trisla-portal -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -z "$POD_NAME" ]; then
    POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
fi

if [ -z "$POD_NAME" ]; then
    echo "❌ Pod não encontrado!"
    echo "Pods disponíveis:"
    kubectl get pods -n trisla
    exit 1
fi

echo "✅ Pod encontrado: $POD_NAME"
echo ""

# 2. Verificar estrutura atual no pod
echo "2️⃣ Verificando estrutura no pod..."
kubectl exec -n trisla $POD_NAME -c trisla-backend -- ls -la /app/apps/api/ 2>/dev/null || \
kubectl exec -n trisla $POD_NAME -c trisla-api -- ls -la /app/apps/api/ 2>/dev/null
echo ""

# 3. Copiar prometheus.py para o pod
echo "3️⃣ Copiando prometheus.py para o pod..."
CONTAINER_NAME="trisla-backend"
kubectl cp apps/api/prometheus.py trisla/$POD_NAME:/app/apps/api/prometheus.py -c $CONTAINER_NAME 2>/dev/null || \
kubectl cp apps/api/prometheus.py trisla/$POD_NAME:/app/apps/api/prometheus.py -c trisla-api 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Arquivo copiado com sucesso"
else
    echo "❌ Erro ao copiar arquivo"
    exit 1
fi
echo ""

# 4. Verificar se httpx está instalado
echo "4️⃣ Verificando dependências..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER_NAME -- pip list | grep httpx || \
kubectl exec -n trisla $POD_NAME -c trisla-api -- pip list | grep httpx

if [ $? -ne 0 ]; then
    echo "⚠️  httpx não encontrado, instalando..."
    kubectl exec -n trisla $POD_NAME -c $CONTAINER_NAME -- pip install httpx || \
    kubectl exec -n trisla $POD_NAME -c trisla-api -- pip install httpx
    echo "✅ httpx instalado"
fi
echo ""

# 5. Verificar se main.py já tem o router
echo "5️⃣ Verificando main.py..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER_NAME -- grep -q "prometheus_router" /app/apps/api/main.py || \
kubectl exec -n trisla $POD_NAME -c trisla-api -- grep -q "prometheus_router" /app/apps/api/main.py

if [ $? -ne 0 ]; then
    echo "⚠️  Router não encontrado no main.py do pod"
    echo "   Precisa adicionar manualmente ou rebuild imagem"
else
    echo "✅ Router já está no main.py"
fi
echo ""

# 6. Reiniciar deployment para aplicar mudanças
echo "6️⃣ Reiniciando deployment..."
kubectl rollout restart deployment/trisla-portal -n trisla 2>/dev/null || \
kubectl rollout restart deployment/$(kubectl get deployment -n trisla | grep portal | awk '{print $1}') -n trisla

echo "⏳ Aguardando rollout..."
kubectl rollout status deployment/trisla-portal -n trisla --timeout=5m || \
kubectl rollout status -n trisla --timeout=5m deployment/$(kubectl get deployment -n trisla | grep portal | awk '{print $1}')
echo ""

# 7. Verificar logs
echo "7️⃣ Verificando logs (últimas 30 linhas)..."
sleep 5
kubectl logs -n trisla -l app=trisla-portal --tail=30 -c trisla-backend | grep -i prometheus || \
kubectl logs -n trisla -l app=trisla-portal --tail=30 -c trisla-api | grep -i prometheus || \
kubectl logs -n trisla -l app=trisla-portal --tail=30 | grep -i prometheus || \
echo "Sem mensagens específicas de prometheus nos logs"
echo ""

# 8. Testar endpoint
echo "8️⃣ Testando endpoint..."
sleep 10
echo "Testando via port-forward (porta 8092)..."
curl -s http://localhost:8092/prometheus/health || echo "⚠️  Port-forward pode não estar configurado"

echo ""
echo "=========================================="
echo "✅ Processo completo!"
echo "=========================================="
echo ""
echo "Para testar via kubectl port-forward:"
echo "  kubectl port-forward -n trisla svc/trisla-portal 8000:8000"
echo "  curl http://localhost:8000/prometheus/health"
echo ""




