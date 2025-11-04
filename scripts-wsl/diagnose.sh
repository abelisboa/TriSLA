#!/bin/bash
# Script de diagnóstico rápido
# Uso: ./scripts-wsl/diagnose.sh

echo "🔍 Diagnóstico do TriSLA Dashboard"
echo "=================================="
echo ""

# Verificar processos
echo "1️⃣ Processos em execução:"
echo ""

# Backend
if pgrep -f "uvicorn.*main:app" > /dev/null; then
    BACKEND_PID=$(pgrep -f "uvicorn.*main:app" | head -1)
    echo "   ✅ Backend rodando (PID: $BACKEND_PID)"
else
    echo "   ❌ Backend NÃO está rodando"
fi

# Frontend
if pgrep -f "vite" > /dev/null; then
    FRONTEND_PID=$(pgrep -f "vite" | head -1)
    echo "   ✅ Frontend rodando (PID: $FRONTEND_PID)"
else
    echo "   ❌ Frontend NÃO está rodando"
fi

# Túnel SSH
if pgrep -f "ssh.*9090.*prometheus" > /dev/null; then
    TUNNEL_PID=$(pgrep -f "ssh.*9090.*prometheus" | head -1)
    echo "   ✅ Túnel SSH rodando (PID: $TUNNEL_PID)"
else
    echo "   ⚪ Túnel SSH não está rodando (opcional)"
fi

echo ""

# Verificar portas
echo "2️⃣ Portas em uso:"
echo ""

for port in 5000 5173 9090; do
    if command -v netstat &> /dev/null; then
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            echo "   ✅ Porta $port está em uso"
        else
            echo "   ❌ Porta $port NÃO está em uso"
        fi
    elif command -v ss &> /dev/null; then
        if ss -tuln 2>/dev/null | grep -q ":$port "; then
            echo "   ✅ Porta $port está em uso"
        else
            echo "   ❌ Porta $port NÃO está em uso"
        fi
    else
        echo "   ⚠️  Não é possível verificar porta $port (netstat/ss não disponível)"
    fi
done

echo ""

# Verificar arquivos do frontend
echo "3️⃣ Arquivos do frontend:"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -f "$PROJECT_DIR/frontend/package.json" ]; then
    echo "   ✅ package.json existe"
else
    echo "   ❌ package.json NÃO encontrado"
fi

if [ -d "$PROJECT_DIR/frontend/node_modules" ]; then
    echo "   ✅ node_modules existe"
else
    echo "   ❌ node_modules NÃO encontrado (execute: cd frontend && npm install)"
fi

if [ -f "$PROJECT_DIR/frontend/index.html" ]; then
    echo "   ✅ index.html existe"
else
    echo "   ❌ index.html NÃO encontrado"
fi

echo ""

# Testar conexões
echo "4️⃣ Testando conexões:"
echo ""

# Backend
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "   ✅ Backend respondendo em http://localhost:5000"
else
    echo "   ❌ Backend NÃO está respondendo"
fi

# Frontend
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "   ✅ Frontend respondendo em http://localhost:5173"
else
    echo "   ❌ Frontend NÃO está respondendo"
fi

echo ""

# Soluções
echo "💡 Soluções:"
echo ""

if ! pgrep -f "vite" > /dev/null; then
    echo "   Para iniciar o frontend:"
    echo "   ./scripts-wsl/start-frontend.sh"
    echo ""
fi

if ! pgrep -f "uvicorn.*main:app" > /dev/null; then
    echo "   Para iniciar o backend:"
    echo "   ./scripts-wsl/start-backend.sh"
    echo ""
fi

echo "   Para reiniciar tudo:"
echo "   ./scripts-wsl/stop-all.sh"
echo "   ./scripts-wsl/start-all.sh"





