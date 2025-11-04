#!/bin/bash
# Script para parar todos os processos do dashboard
# Uso: ./scripts-wsl/stop-all.sh

echo "🛑 Parando processos do TriSLA Dashboard..."
echo ""

# Parar backend
if pgrep -f "uvicorn.*main:app" > /dev/null; then
    BACKEND_PIDS=$(pgrep -f "uvicorn.*main:app")
    echo "   Parando backend (PIDs: $BACKEND_PIDS)..."
    pkill -f "uvicorn.*main:app"
    echo "   ✅ Backend parado"
else
    echo "   ℹ️  Backend não está rodando"
fi

# Parar frontend
if pgrep -f "vite" > /dev/null; then
    FRONTEND_PIDS=$(pgrep -f "vite")
    echo "   Parando frontend (PIDs: $FRONTEND_PIDS)..."
    pkill -f "vite"
    echo "   ✅ Frontend parado"
else
    echo "   ℹ️  Frontend não está rodando"
fi

# Parar túnel SSH
if pgrep -f "ssh.*9090.*prometheus" > /dev/null; then
    TUNNEL_PIDS=$(pgrep -f "ssh.*9090.*prometheus")
    echo "   Parando túnel SSH (PIDs: $TUNNEL_PIDS)..."
    pkill -f "ssh.*9090.*prometheus"
    echo "   ✅ Túnel SSH parado"
else
    echo "   ℹ️  Túnel SSH não está rodando"
fi

echo ""
echo "✅ Todos os processos parados!"

