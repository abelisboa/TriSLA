#!/bin/bash

PORTAL_PATH="/mnt/c/Users/USER/Documents/TriSLA-clean/trisla-portal"
BACKEND_DIR="$PORTAL_PATH/backend"
FRONTEND_DIR="$PORTAL_PATH/frontend"
BACKEND_PORT=8001
FRONTEND_PORT=3000

clear

banner() {
    echo "============================================================"
    echo "                TRI-SLA PORTAL MANAGER v1.0                 "
    echo "============================================================"
}

is_wsl2() {
    if [ -f /proc/version ]; then
        grep -qi "microsoft\|wsl" /proc/version && return 0
    fi
    return 1
}

start_backend() {
    echo "[INFO] Iniciando Backend FastAPI (Modo DESENVOLVIMENTO)..."
    cd "$BACKEND_DIR" || exit
    
    if is_wsl2; then
        echo "[WARN] WSL2 detectado - Monitore uso de memória"
    fi
    
    # Verificar e liberar porta se ocupada
    if lsof -i :$BACKEND_PORT >/dev/null 2>&1; then
        echo "[WARN] Porta $BACKEND_PORT ocupada. Matando processo..."
        kill -9 $(lsof -t -i :$BACKEND_PORT) 2>/dev/null || true
        sleep 1
    fi
    
    if [ ! -f "venv/bin/activate" ]; then
        echo "[ERRO] venv não encontrado em $BACKEND_DIR/venv"
        echo ""
        echo "[INFO] Para criar o ambiente virtual com todas as dependências:"
        echo "  cd $BACKEND_DIR"
        echo "  bash scripts/rebuild_venv.sh"
        echo ""
        exit 1
    fi
    
    source venv/bin/activate
    echo "[INFO] Usando launcher seguro (run.py) - reload limitado a src/"
    python3 run.py
}

start_backend_prod() {
    echo "[INFO] Iniciando Backend FastAPI (Modo PRODUÇÃO - NASP)..."
    cd "$BACKEND_DIR" || exit
    
    if [ ! -f "venv/bin/activate" ]; then
        echo "[ERRO] venv não encontrado em $BACKEND_DIR/venv"
        echo ""
        echo "[INFO] Para criar o ambiente virtual com todas as dependências:"
        echo "  cd $BACKEND_DIR"
        echo "  bash scripts/rebuild_venv.sh"
        echo ""
        exit 1
    fi
    
    source venv/bin/activate
    BACKEND_MODE=prod python3 run.py
}

start_frontend() {
    echo "[INFO] Iniciando Frontend Next.js..."
    cd "$FRONTEND_DIR" || exit
    npm run dev
}

kill_backend_port() {
    echo "[INFO] Liberando porta $BACKEND_PORT..."
    lsof -ti :$BACKEND_PORT | xargs kill -9 2>/dev/null
    echo "[OK] Porta $BACKEND_PORT liberada."
}

kill_frontend_port() {
    echo "[INFO] Liberando porta $FRONTEND_PORT..."
    lsof -ti :$FRONTEND_PORT | xargs kill -9 2>/dev/null
    echo "[OK] Porta $FRONTEND_PORT liberada."
}

stop_all() {
    echo "[INFO] Encerrando Backend e Frontend..."
    pkill -f "uvicorn.*$BACKEND_PORT" 2>/dev/null
    pkill -f "run.py" 2>/dev/null
    pkill -f "next.*$FRONTEND_PORT" 2>/dev/null
    kill_backend_port
    kill_frontend_port
    echo "[OK] Serviços interrompidos."
}

show_urls() {
    echo ""
    echo "============================================================"
    echo "                   ACESSO AO PORTAL TRI-SLA                 "
    echo "============================================================"
    echo "Frontend:   http://localhost:$FRONTEND_PORT"
    echo "Backend:    http://localhost:$BACKEND_PORT"
    echo "API Docs:   http://localhost:$BACKEND_PORT/docs"
    echo "============================================================"
    echo ""
}

menu() {
    banner
    echo "1) Iniciar Backend (DEV - com reload seguro)"
    echo "2) Iniciar Frontend"
    echo "3) Liberar porta Backend ($BACKEND_PORT)"
    echo "4) Liberar porta Frontend ($FRONTEND_PORT)"
    echo "5) Parar tudo"
    echo "6) Mostrar URLs do Portal"
    echo "7) Iniciar Backend (PROD - NASP sem reload)"
    echo "0) Sair"
    echo "============================================================"
    read -rp "Escolha uma opção: " opt

    case $opt in
        1) start_backend ;;
        2) start_frontend ;;
        3) kill_backend_port ;;
        4) kill_frontend_port ;;
        5) stop_all ;;
        6) show_urls ;;
        7) start_backend_prod ;;
        0) exit 0 ;;
        *) echo "[ERRO] Opção inválida!" ;;
    esac

    echo ""
    read -rp "Pressione ENTER para voltar ao menu..."
    menu
}

menu
