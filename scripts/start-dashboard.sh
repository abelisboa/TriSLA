#!/usr/bin/env bash
# ============================================================
# Start Dashboard - TriSLA Dashboard v3.2.4
# Inicia o dashboard localmente (desenvolvimento)
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "======================================================"
echo "🚀 Iniciando TriSLA Dashboard v3.2.4"
echo "======================================================"
echo ""

# Verificar se estamos no diretório correto
if [ ! -d "$BASE_DIR/backend" ] || [ ! -d "$BASE_DIR/frontend" ]; then
    echo "❌ Execute este script a partir do diretório raiz do projeto"
    exit 1
fi

# Backend
echo "🔧 Iniciando Backend..."
cd "$BASE_DIR/backend"
if [ ! -f "main.py" ]; then
    echo "❌ Arquivo main.py não encontrado"
    exit 1
fi

# Verificar se já está rodando
if pgrep -f "python.*main.py" > /dev/null; then
    echo "⚠️  Backend já está rodando"
else
    nohup python3 main.py > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo "✅ Backend iniciado (PID: $BACKEND_PID)"
    echo "   Logs: $BASE_DIR/backend.log"
fi

# Frontend
echo "🔧 Iniciando Frontend..."
cd "$BASE_DIR/frontend"
if [ ! -f "package.json" ]; then
    echo "❌ Arquivo package.json não encontrado"
    exit 1
fi

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências do frontend..."
    npm install
fi

# Verificar se já está rodando
if pgrep -f "vite.*5174" > /dev/null; then
    echo "⚠️  Frontend já está rodando"
else
    nohup npm run dev -- --port=5174 --host=0.0.0.0 > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "✅ Frontend iniciado (PID: $FRONTEND_PID)"
    echo "   Logs: $BASE_DIR/frontend.log"
fi

echo ""
echo "======================================================"
echo "✅ Dashboard iniciado!"
echo "======================================================"
echo ""
echo "Backend:  http://localhost:5000"
echo "Frontend: http://localhost:5174"
echo ""
echo "Para parar:"
echo "  pkill -f 'python.*main.py'"
echo "  pkill -f 'vite.*5174'"
echo ""
