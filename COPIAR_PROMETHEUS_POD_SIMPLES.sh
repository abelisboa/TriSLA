#!/bin/bash
# Script simples para copiar prometheus.py para o pod

set -e

echo "=========================================="
echo "🚀 Copiando prometheus.py para Pod"
echo "=========================================="
echo ""

# 1. Identificar pod
POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
if [ -z "$POD_NAME" ]; then
    echo "❌ Pod não encontrado!"
    exit 1
fi

CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')
echo "Pod: $POD_NAME"
echo "Container: $CONTAINER"
echo ""

# 2. Verificar estrutura
echo "🔍 Verificando estrutura do pod..."
echo ""

echo "Opção 1: /app/main.py (raiz)"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- test -f /app/main.py 2>/dev/null && echo "  ✅ Existe" || echo "  ❌ Não existe"

echo "Opção 2: /app/apps/api/main.py"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- test -f /app/apps/api/main.py 2>/dev/null && echo "  ✅ Existe" || echo "  ❌ Não existe"

echo "Opção 3: /app/api/main.py"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- test -f /app/api/main.py 2>/dev/null && echo "  ✅ Existe" || echo "  ❌ Não existe"
echo ""

# 3. Determinar caminho correto
MAIN_PATH=""
if kubectl exec -n trisla $POD_NAME -c $CONTAINER -- test -f /app/apps/api/main.py 2>/dev/null; then
    MAIN_PATH="/app/apps/api/main.py"
    TARGET_DIR="/app/apps/api"
elif kubectl exec -n trisla $POD_NAME -c $CONTAINER -- test -f /app/api/main.py 2>/dev/null; then
    MAIN_PATH="/app/api/main.py"
    TARGET_DIR="/app/api"
elif kubectl exec -n trisla $POD_NAME -c $CONTAINER -- test -f /app/main.py 2>/dev/null; then
    MAIN_PATH="/app/main.py"
    TARGET_DIR="/app"
else
    echo "⚠️  main.py não encontrado. Tentando criar em /app/apps/api..."
    TARGET_DIR="/app/apps/api"
    kubectl exec -n trisla $POD_NAME -c $CONTAINER -- mkdir -p $TARGET_DIR
fi

echo "✅ Usando diretório: $TARGET_DIR"
echo ""

# 4. Verificar se arquivo local existe
if [ ! -f "apps/api/prometheus.py" ]; then
    echo "❌ Arquivo apps/api/prometheus.py não encontrado localmente!"
    exit 1
fi

# 5. Copiar usando base64 (mais confiável)
echo "📦 Copiando arquivo usando base64..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- bash -c "
  mkdir -p $TARGET_DIR
  cat > $TARGET_DIR/prometheus.py << 'PYEOF'
$(cat apps/api/prometheus.py)
PYEOF
"

if [ $? -eq 0 ]; then
    echo "✅ Arquivo copiado com sucesso!"
else
    echo "❌ Erro ao copiar arquivo"
    exit 1
fi
echo ""

# 6. Verificar
echo "🔍 Verificando arquivo no pod..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh $TARGET_DIR/prometheus.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- head -5 $TARGET_DIR/prometheus.py
echo ""

# 7. Instalar httpx (se necessário)
echo "📦 Verificando httpx..."
if kubectl exec -n trisla $POD_NAME -c $CONTAINER -- pip list | grep -q httpx 2>/dev/null; then
    echo "✅ httpx já instalado"
else
    echo "⚠️  httpx não encontrado. Tentando instalar..."
    kubectl exec -n trisla $POD_NAME -c $CONTAINER -- pip install httpx 2>/dev/null || \
    echo "⚠️  Não foi possível instalar httpx (problema de rede). Instale manualmente ou adicione ao requirements.txt"
fi
echo ""

# 8. Verificar main.py
echo "🔍 Verificando se main.py precisa ser atualizado..."
if kubectl exec -n trisla $POD_NAME -c $CONTAINER -- grep -q "prometheus_router" $TARGET_DIR/main.py 2>/dev/null; then
    echo "✅ Router já está no main.py"
else
    echo "⚠️  Router não encontrado no main.py"
    echo "   Precisa adicionar manualmente ou copiar main.py também"
    echo ""
    echo "   Adicione ao main.py:"
    echo ""
    echo "   # Prometheus router"
    echo "   try:"
    echo "       from prometheus import router as prometheus_router"
    echo "       app.include_router(prometheus_router)"
    echo "       log.info(\"Prometheus router habilitado em /prometheus\")"
    echo "   except Exception as e:"
    echo "       log.warning(\"Prometheus router não carregado: %s\", e)"
fi
echo ""

echo "=========================================="
echo "✅ Processo completo!"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "1. Atualizar main.py se necessário"
echo "2. Reiniciar deployment: kubectl rollout restart deployment/trisla-portal -n trisla"
echo "3. Testar: curl http://localhost:8092/prometheus/health"
echo ""




