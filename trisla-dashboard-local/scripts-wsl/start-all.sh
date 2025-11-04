#!/bin/bash
# Script para iniciar tudo: túnel SSH, backend e frontend
# Uso: ./scripts-wsl/start-all.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 Iniciando TriSLA Dashboard Local (WSL)..."
echo ""
echo "ℹ️  O dashboard funciona sem conexão SSH."
echo "   Para conectar ao Prometheus do node1, execute: ./scripts-wsl/start-ssh-tunnel.sh"
echo ""

# 1. Verificar se backend está rodando
echo "1️⃣ Verificando backend..."
if pgrep -f "uvicorn.*main:app" > /dev/null; then
    echo "   ✅ Backend já está rodando"
else
    echo "   Iniciando backend..."
    cd "$PROJECT_DIR/backend"
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    python -m uvicorn main:app --reload --port 5000 &
    BACKEND_PID=$!
    sleep 3
    if ps -p $BACKEND_PID > /dev/null; then
        echo "   ✅ Backend iniciado em http://localhost:5000 (PID: $BACKEND_PID)"
    else
        echo "   ❌ Falha ao iniciar backend"
        exit 1
    fi
fi
echo ""

# 2. Verificar se frontend está rodando
echo "2️⃣ Verificando frontend..."
if pgrep -f "vite" > /dev/null; then
    echo "   ✅ Frontend já está rodando"
else
    echo "   Iniciando frontend..."
    cd "$PROJECT_DIR/frontend"
    npm run dev &
    FRONTEND_PID=$!
    sleep 5
    if ps -p $FRONTEND_PID > /dev/null; then
        echo "   ✅ Frontend iniciado em http://localhost:5173 (PID: $FRONTEND_PID)"
    else
        echo "   ❌ Falha ao iniciar frontend"
        exit 1
    fi
fi
echo ""

echo "✅ Tudo iniciado!"
echo ""
echo "📊 Acesse o dashboard em:"
echo "   http://localhost:5173"
echo ""
echo "🔧 APIs disponíveis:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:5000"
echo "   Swagger:  http://localhost:5000/docs"
echo "   Prometheus (via túnel, se configurado): http://localhost:9090"
echo ""
echo "Para parar, pressione Ctrl+C e execute: ./scripts-wsl/stop-all.sh"

