#!/bin/bash
# Script interativo para gerenciar TriSLA Dashboard
# Uso: ./scripts-wsl/dashboard-menu.sh

set -e

DASHBOARD_DIR=~/trisla-dashboard-local
BACKEND_PORT=5000
FRONTEND_PORT=5173

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

cd "$DASHBOARD_DIR" 2>/dev/null || {
    echo -e "${RED}❌ Erro: Diretório $DASHBOARD_DIR não encontrado${NC}"
    exit 1
}

check_port() {
    local port=$1
    lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1
}

get_pid() {
    local pattern=$1
    pgrep -f "$pattern" | head -1
}

open_browser() {
    local url=$1
    if command -v wslview > /dev/null; then
        wslview "$url" 2>/dev/null &
    elif command -v cmd.exe > /dev/null; then
        cmd.exe /c start "$url" 2>/dev/null &
    elif command -v xdg-open > /dev/null; then
        xdg-open "$url" 2>/dev/null &
    else
        echo -e "${YELLOW}⚠️  Abra manualmente: $url${NC}"
    fi
}

start_backend() {
    if check_port $BACKEND_PORT; then
        echo -e "${YELLOW}⚠️  Backend já está rodando na porta $BACKEND_PORT${NC}"
        return 1
    fi

    if [ ! -d "backend/venv" ]; then
        echo -e "${RED}❌ Virtual environment não encontrado${NC}"
        echo "   Execute: cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        return 1
    fi

    cd backend
    source venv/bin/activate 2>/dev/null || {
        echo -e "${RED}❌ Erro ao ativar venv${NC}"
        cd ..
        return 1
    }
    
    echo -e "${CYAN}🚀 Iniciando backend...${NC}"
    uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > ../backend.log 2>&1 &
    BACKEND_PID=$!
    
    echo $BACKEND_PID > ../backend.pid
    cd ..
    
    sleep 3
    if check_port $BACKEND_PORT; then
        echo -e "${GREEN}✅ Backend iniciado (PID: $BACKEND_PID)${NC}"
        return 0
    else
        echo -e "${RED}❌ Erro ao iniciar backend${NC}"
        echo -e "${YELLOW}   Verifique logs: tail -f backend.log${NC}"
        if [ -f "backend.log" ]; then
            echo -e "${CYAN}   Últimas linhas do log:${NC}"
            tail -n 10 backend.log | grep -i error || tail -n 5 backend.log
        fi
        return 1
    fi
}

stop_backend() {
    local pid=$(get_pid "uvicorn.*main:app")
    if [ -n "$pid" ]; then
        echo -e "${CYAN}🛑 Parando backend (PID: $pid)...${NC}"
        kill $pid 2>/dev/null
        sleep 1
        rm -f backend.pid
        echo -e "${GREEN}✅ Backend parado${NC}"
    else
        echo -e "${YELLOW}ℹ️  Backend não está rodando${NC}"
    fi
}

start_frontend() {
    if check_port $FRONTEND_PORT; then
        echo -e "${YELLOW}⚠️  Frontend já está rodando na porta $FRONTEND_PORT${NC}"
        return 1
    fi

    if [ ! -d "frontend/node_modules" ]; then
        echo -e "${RED}❌ Dependências do frontend não instaladas${NC}"
        echo "   Execute: cd frontend && npm install"
        return 1
    fi

    if [ ! -f "frontend/package.json" ]; then
        echo -e "${RED}❌ package.json não encontrado${NC}"
        return 1
    fi

    if ! command -v npm > /dev/null; then
        echo -e "${RED}❌ npm não encontrado. Instale Node.js primeiro.${NC}"
        return 1
    fi

    cd frontend
    
    echo -e "${CYAN}🚀 Iniciando frontend...${NC}"
    npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    echo $FRONTEND_PID > ../frontend.pid
    cd ..
    
    sleep 4
    if check_port $FRONTEND_PORT; then
        echo -e "${GREEN}✅ Frontend iniciado (PID: $FRONTEND_PID)${NC}"
        return 0
    else
        echo -e "${RED}❌ Erro ao iniciar frontend${NC}"
        echo -e "${YELLOW}   Verifique logs: tail -f frontend.log${NC}"
        if [ -f "frontend.log" ]; then
            echo -e "${CYAN}   Últimas linhas do log:${NC}"
            tail -n 10 frontend.log | grep -i error || tail -n 5 frontend.log
        fi
        return 1
    fi
}

stop_frontend() {
    local pid=$(get_pid "vite")
    if [ -n "$pid" ]; then
        echo -e "${CYAN}🛑 Parando frontend (PID: $pid)...${NC}"
        kill $pid 2>/dev/null
        sleep 1
        rm -f frontend.pid
        echo -e "${GREEN}✅ Frontend parado${NC}"
    else
        echo -e "${YELLOW}ℹ️  Frontend não está rodando${NC}"
    fi
}

show_status() {
    echo -e "${CYAN}📊 Status dos Serviços:${NC}"
    echo ""
    
    if check_port $BACKEND_PORT; then
        local pid=$(get_pid "uvicorn.*main:app")
        echo -e "${GREEN}✅ Backend: Rodando (PID: $pid) - http://localhost:$BACKEND_PORT${NC}"
    else
        echo -e "${RED}❌ Backend: Parado${NC}"
    fi
    
    if check_port $FRONTEND_PORT; then
        local pid=$(get_pid "vite")
        echo -e "${GREEN}✅ Frontend: Rodando (PID: $pid) - http://localhost:$FRONTEND_PORT${NC}"
    else
        echo -e "${RED}❌ Frontend: Parado${NC}"
    fi
    echo ""
}

show_menu() {
    clear
    echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   TriSLA Dashboard - Menu Principal   ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
    echo ""
    show_status
    
    echo -e "${CYAN}🌐 ABRIR NO NAVEGADOR:${NC}"
    echo "  1) Frontend Dashboard     (http://localhost:$FRONTEND_PORT)"
    echo "  2) Backend API            (http://localhost:$BACKEND_PORT)"
    echo "  3) Swagger Docs            (http://localhost:$BACKEND_PORT/docs)"
    echo "  4) Health Check            (http://localhost:$BACKEND_PORT/health)"
    echo ""
    echo -e "${CYAN}🚀 INICIAR SERVIÇOS:${NC}"
    echo "  5) Iniciar Backend"
    echo "  6) Iniciar Frontend"
    echo "  7) Iniciar Tudo (Backend + Frontend)"
    echo ""
    echo -e "${CYAN}🛑 PARAR SERVIÇOS:${NC}"
    echo "  8) Parar Backend"
    echo "  9) Parar Frontend"
    echo "  10) Parar Tudo"
    echo ""
    echo -e "${CYAN}🔄 REINICIAR:${NC}"
    echo "  11) Reiniciar Backend"
    echo "  12) Reiniciar Frontend"
    echo "  13) Reiniciar Tudo"
    echo ""
    echo -e "${CYAN}📋 INFORMAÇÕES:${NC}"
    echo "  14) Ver Logs do Backend"
    echo "  15) Ver Logs do Frontend"
    echo "  16) Status Detalhado"
    echo ""
    echo -e "${YELLOW}  0) Sair${NC}"
    echo ""
}

while true; do
    show_menu
    read -p "Escolha uma opção (0-16): " choice
    echo ""
    
    case $choice in
        1)
            open_browser "http://localhost:$FRONTEND_PORT"
            echo -e "${GREEN}✅ Navegador aberto${NC}"
            ;;
        2)
            open_browser "http://localhost:$BACKEND_PORT"
            echo -e "${GREEN}✅ Navegador aberto${NC}"
            ;;
        3)
            open_browser "http://localhost:$BACKEND_PORT/docs"
            echo -e "${GREEN}✅ Navegador aberto${NC}"
            ;;
        4)
            open_browser "http://localhost:$BACKEND_PORT/health"
            echo -e "${GREEN}✅ Navegador aberto${NC}"
            ;;
        5)
            start_backend
            ;;
        6)
            start_frontend
            ;;
        7)
            if start_backend; then
                sleep 2
                if start_frontend; then
                    echo -e "${GREEN}✅ Todos os serviços iniciados!${NC}"
                else
                    echo -e "${YELLOW}⚠️  Backend iniciado, mas frontend falhou${NC}"
                    echo -e "${YELLOW}   Execute opção 15 para ver logs do frontend${NC}"
                fi
            else
                echo -e "${RED}❌ Falha ao iniciar backend${NC}"
                echo -e "${YELLOW}   Execute opção 14 para ver logs do backend${NC}"
            fi
            ;;
        8)
            stop_backend
            ;;
        9)
            stop_frontend
            ;;
        10)
            stop_backend
            stop_frontend
            echo -e "${GREEN}✅ Todos os serviços parados${NC}"
            ;;
        11)
            stop_backend
            sleep 1
            start_backend
            ;;
        12)
            stop_frontend
            sleep 1
            start_frontend
            ;;
        13)
            echo -e "${CYAN}🔄 Reiniciando todos os serviços...${NC}"
            stop_backend
            stop_frontend
            sleep 3
            if start_backend; then
                sleep 2
                if start_frontend; then
                    echo -e "${GREEN}✅ Todos os serviços reiniciados!${NC}"
                else
                    echo -e "${YELLOW}⚠️  Backend reiniciado, mas frontend falhou${NC}"
                    echo -e "${YELLOW}   Execute opção 16 para ver logs${NC}"
                fi
            else
                echo -e "${RED}❌ Falha ao reiniciar backend${NC}"
                echo -e "${YELLOW}   Execute opção 16 para ver logs${NC}"
            fi
            ;;
        14)
            if [ -f "backend.log" ]; then
                tail -n 50 backend.log
            else
                echo -e "${YELLOW}ℹ️  Log não encontrado${NC}"
            fi
            ;;
        15)
            if [ -f "frontend.log" ]; then
                tail -n 50 frontend.log
            else
                echo -e "${YELLOW}ℹ️  Log não encontrado${NC}"
            fi
            ;;
        16)
            show_status
            if [ -f "backend.pid" ]; then
                echo "Backend PID: $(cat backend.pid)"
            fi
            if [ -f "frontend.pid" ]; then
                echo "Frontend PID: $(cat frontend.pid)"
            fi
            ;;
        0)
            echo -e "${GREEN}👋 Até logo!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Opção inválida!${NC}"
            ;;
    esac
    
    echo ""
    read -p "Pressione ENTER para continuar..."
done
