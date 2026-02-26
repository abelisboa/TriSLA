#!/bin/bash

# ===============================
# TriSLA Observability Manager v5
# ===============================

PPP_USER="porvir5g"
PPP_HOST="ppgca.unisinos.br"
NODE_REAL="node1"

# PORTAS LOCAIS
GRAFANA=3000
PROM=9090
TEMPO=3100
TRISLA_UI=8088

# ===============================
kill_existing() {
    echo "[INFO] Encerrando túneis e port-forwards antigos..."
    pkill -f "ssh -L" 2>/dev/null
    pkill -f "kubectl port-forward" 2>/dev/null
}

# ===============================
start_tunnel() {
    echo "[INFO] Iniciando túnel principal para API Server..."
    ssh -f -N \
        -o ExitOnForwardFailure=yes \
        -o ProxyCommand="ssh -W %h:%p $PPP_USER@$PPP_HOST" \
        -L 6443:127.0.0.1:6443 \
        $PPP_USER@$NODE_REAL

    if [ $? -ne 0 ]; then
        echo "[ERRO] Falha ao criar túnel para API Server."
        exit 1
    fi

    echo "[OK] Túnel criado → https://127.0.0.1:6443"
}

# ===============================
start_port_forward() {
    echo "[INFO] Abrindo port-forward dos serviços TriSLA..."
    
    # Grafana
    kubectl -n monitoring port-forward svc/monitoring-grafana $GRAFANA:80 --address 0.0.0.0 >/dev/null 2>&1 &
    sleep 1

    # Prometheus
    kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus $PROM:9090 --address 0.0.0.0 >/dev/null 2>&1 &
    sleep 1

    # Tempo
    kubectl -n monitoring port-forward svc/tempo $TEMPO:3100 --address 0.0.0.0 >/dev/null 2>&1 &
    sleep 1

    # TriSLA Dashboard
    kubectl -n trisla port-forward svc/trisla-ui-dashboard $TRISLA_UI:80 --address 0.0.0.0 >/dev/null 2>&1 &
    sleep 1

    echo "[OK] Port-forwards criados."
}

# ===============================
health_check() {
    echo "=== HEALTH CHECK ==="
    
    curl -k --silent https://127.0.0.1:6443/version >/dev/null
    echo "API Server:     $( [ $? -eq 0 ] && echo OK || echo FAIL )"

    curl --silent http://127.0.0.1:$GRAFANA/login >/dev/null
    echo "Grafana:        $( [ $? -eq 0 ] && echo OK || echo FAIL )"

    curl --silent http://127.0.0.1:$PROM/api/v1/status/runtimeinfo >/dev/null
    echo "Prometheus:     $( [ $? -eq 0 ] && echo OK || echo FAIL )"

    curl --silent http://127.0.0.1:$TEMPO/ready >/dev/null
    echo "Tempo:          $( [ $? -eq 0 ] && echo OK || echo FAIL )"

    curl --silent http://127.0.0.1:$TRISLA_UI >/dev/null
    echo "TriSLA UI:      $( [ $? -eq 0 ] && echo OK || echo FAIL )"

    echo "===================="
}

# ===============================
open_browser() {
    echo "[INFO] Abrindo navegador..."
    xdg-open http://localhost:$GRAFANA >/dev/null 2>&1
    xdg-open http://localhost:$PROM >/dev/null 2>&1
    xdg-open http://localhost:$TEMPO >/dev/null 2>&1
    xdg-open http://localhost:$TRISLA_UI >/dev/null 2>&1
}

# ===============================
menu() {
    clear
    echo "=========================================="
    echo " TriSLA Observability Manager — ULTRA v5"
    echo "=========================================="
    echo "1) START  — iniciar túnel + port-forward"
    echo "2) STOP   — encerrar conexões"
    echo "3) RESTART"
    echo "4) HEALTH CHECK"
    echo "5) ABRIR NO NAVEGADOR"
    echo "0) SAIR"
    echo "=========================================="
    echo -n "Escolha: "
}

# ===============================
while true; do
    menu
    read opt

    case $opt in
        1)
            kill_existing
            start_tunnel
            start_port_forward
            health_check
            ;;
        2)
            kill_existing
            echo "[OK] Tudo parado."
            ;;
        3)
            kill_existing
            start_tunnel
            start_port_forward
            health_check
            ;;
        4)
            health_check
            ;;
        5)
            open_browser
            ;;
        0)
            kill_existing
            exit 0
            ;;
        *)
            echo "Opção inválida."
            ;;
    esac
done
