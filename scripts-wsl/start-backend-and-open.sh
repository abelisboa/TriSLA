#!/bin/bash
# Script para iniciar backend e abrir no navegador
# Uso: ./scripts-wsl/start-backend-and-open.sh

set -e

cd ~/trisla-dashboard-local

echo "🚀 Iniciando TriSLA Backend..."
echo ""

# Verificar se estamos no diretório correto
if [ ! -f "backend/main.py" ]; then
    echo "❌ Erro: Execute este script da raiz do projeto (trisla-dashboard-local)"
    exit 1
fi

# Verificar se venv existe
if [ ! -d "backend/venv" ]; then
    echo "❌ Erro: Virtual environment não encontrado em backend/venv"
    echo "   Execute: cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Verificar se backend já está rodando
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Porta 5000 já está em uso!"
    echo "   O backend pode já estar rodando."
    echo ""
    read -p "Deseja abrir o navegador mesmo assim? (S/N) " response
    if [ "$response" = "S" ] || [ "$response" = "s" ]; then
        if command -v xdg-open > /dev/null; then
            xdg-open "http://localhost:5000" 2>/dev/null &
        elif command -v wslview > /dev/null; then
            wslview "http://localhost:5000" 2>/dev/null &
        else
            echo "❌ Não foi possível abrir o navegador automaticamente"
            echo "   Abra manualmente: http://localhost:5000"
        fi
    fi
    exit 0
fi

cd backend

echo "1️⃣ Ativando virtual environment..."
source venv/bin/activate

echo "2️⃣ Iniciando backend FastAPI..."
echo ""

# Iniciar backend em background
uvicorn main:app --host 0.0.0.0 --port 5000 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!

echo "   ✅ Backend iniciado (PID: $BACKEND_PID)"
echo ""

# Aguardar alguns segundos para o backend iniciar
echo "3️⃣ Aguardando backend iniciar..."
sleep 3

# Verificar se backend está respondendo
MAX_RETRIES=10
RETRY_COUNT=0
BACKEND_READY=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ] && [ "$BACKEND_READY" = false ]; do
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        BACKEND_READY=true
        echo "   ✅ Backend está respondendo!"
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "   ⏳ Tentativa $RETRY_COUNT/$MAX_RETRIES..."
        sleep 1
    fi
done

if [ "$BACKEND_READY" = false ]; then
    echo "   ⚠️  Backend pode não estar pronto, mas tentando abrir navegador..."
fi

echo ""
echo "4️⃣ Abrindo navegador em http://localhost:5000..."

# Tentar abrir navegador (funciona no WSL se Windows estiver configurado)
if command -v wslview > /dev/null; then
    wslview "http://localhost:5000" 2>/dev/null &
elif command -v cmd.exe > /dev/null; then
    cmd.exe /c start "http://localhost:5000" 2>/dev/null &
elif command -v xdg-open > /dev/null; then
    xdg-open "http://localhost:5000" 2>/dev/null &
else
    echo "⚠️  Não foi possível abrir o navegador automaticamente"
    echo "   Abra manualmente: http://localhost:5000"
fi

echo ""
echo "✅ Backend rodando e navegador aberto!"
echo ""
echo "📊 URLs disponíveis:"
echo "   API:      http://localhost:5000"
echo "   Health:   http://localhost:5000/health"
echo "   Swagger:  http://localhost:5000/docs"
echo "   Redoc:    http://localhost:5000/redoc"
echo ""
echo "📝 Logs do backend: tail -f ~/trisla-dashboard-local/backend.log"
echo ""
echo "⚠️  Para parar o backend, execute:"
echo "   kill $BACKEND_PID"
echo "   ou use: ./scripts-wsl/stop-all.sh"
echo ""

# Salvar PID para poder parar depois
echo $BACKEND_PID > ../backend.pid





