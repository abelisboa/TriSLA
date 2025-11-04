#!/usr/bin/env bash
# ============================================================
# Test Local - TriSLA Dashboard v3.2.4
# Testa os serviços localmente
# ============================================================

set -e

echo "======================================================"
echo "🧪 Test Local - TriSLA Dashboard v3.2.4"
echo "======================================================"
echo ""

# Verificar se os containers estão rodando
if ! docker ps | grep -q "trisla-dashboard-backend"; then
    echo "❌ Backend container não está rodando"
    echo "   Execute: docker-compose up -d"
    exit 1
fi

if ! docker ps | grep -q "trisla-dashboard-frontend"; then
    echo "❌ Frontend container não está rodando"
    echo "   Execute: docker-compose up -d"
    exit 1
fi

echo "✅ Containers estão rodando"
echo ""

# Testar Backend
echo "🔍 Testando Backend (http://localhost:5000)..."
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health || echo "000")
if [ "$BACKEND_HEALTH" == "200" ]; then
    echo "✅ Backend: OK (HTTP $BACKEND_HEALTH)"
else
    echo "❌ Backend: FALHOU (HTTP $BACKEND_HEALTH)"
fi

# Testar Backend Status
BACKEND_STATUS=$(curl -s http://localhost:5000/status | jq -r '.status' 2>/dev/null || echo "error")
if [ "$BACKEND_STATUS" == "operational" ]; then
    echo "✅ Backend Status: OK"
else
    echo "⚠️  Backend Status: $BACKEND_STATUS"
fi

# Testar Métricas
METRICS=$(curl -s http://localhost:5000/metrics | head -n 1)
if [ -n "$METRICS" ]; then
    echo "✅ Métricas Prometheus: OK"
else
    echo "❌ Métricas Prometheus: FALHOU"
fi

echo ""

# Testar Frontend
echo "🔍 Testando Frontend (http://localhost:5174)..."
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5174/health || echo "000")
if [ "$FRONTEND_HEALTH" == "200" ]; then
    echo "✅ Frontend: OK (HTTP $FRONTEND_HEALTH)"
else
    echo "❌ Frontend: FALHOU (HTTP $FRONTEND_HEALTH)"
fi

echo ""
echo "======================================================"
echo "📊 Resumo dos Testes"
echo "======================================================"
echo ""
echo "Backend API:    http://localhost:5000"
echo "Backend Health: http://localhost:5000/health"
echo "Backend Status: http://localhost:5000/status"
echo "Métricas:       http://localhost:5000/metrics"
echo ""
echo "Frontend:       http://localhost:5174"
echo ""
echo "======================================================"
