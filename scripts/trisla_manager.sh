#!/bin/bash

function connect() {
ssh -t porvir5g@ppgca.unisinos.br "
    ssh -t node006 '
        $1
        bash
    '
"
}

function start_pf() {
connect "
    kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80 > /dev/null 2>&1 &
    kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090 > /dev/null 2>&1 &
    kubectl -n monitoring port-forward svc/tempo 3100:3100 > /dev/null 2>&1 &
    kubectl -n trisla port-forward svc/trisla-ui-dashboard 8088:80 > /dev/null 2>&1 &
"
}

function stop_pf() {
connect "
    kill \$(lsof -t -i:3000) 2>/dev/null
    kill \$(lsof -t -i:9090) 2>/dev/null
    kill \$(lsof -t -i:3100) 2>/dev/null
    kill \$(lsof -t -i:8088) 2>/dev/null
"
}

function status() {
connect "
    kubectl get nodes
    kubectl get ns
    kubectl -n trisla get pods
    kubectl -n monitoring get pods
"
}

function logs() {
connect "
    kubectl -n trisla logs -l app=$1 --tail=200
"
}

function restart() {
connect "
    kubectl -n trisla rollout restart deployment/$1
    kubectl -n trisla rollout status deployment/$1
"
}

function audit() {
connect "
    cd /home/porvir5g/gtp5g/trisla/scripts
    ./audit-observability.sh
"
}

function health() {
connect "
    kubectl -n trisla exec \$(kubectl -n trisla get pod -l app=decision-engine -o jsonpath='{.items[0].metadata.name}') -- curl -s http://localhost:8082/healthcheck
"
}

function e2e() {
connect "
    cd /home/porvir5g/gtp5g/trisla/scripts
    python3 e2e_test_intents.py
"
}

while true; do
clear
echo "=============================="
echo "   GERENCIADOR TRISLA 3.7.9   "
echo "=============================="
echo "1) Start (Port-Forward + Ambiente)"
echo "2) Stop  (Encerrar Port-Forwards)"
echo "3) Status Completo"
echo "4) Logs por módulo"
echo "5) Restart módulo"
echo "6) Health-check"
echo "7) Auditoria Completa"
echo "8) Teste E2E (Intents)"
echo "9) Sair"
echo "=============================="
read -p "Escolha uma opção: " op

case $op in
    1) start_pf ;;
    2) stop_pf ;;
    3) status ;;
    4) read -p 'Nome do módulo (ex: decision-engine): ' mod; logs $mod ;;
    5) read -p 'Deployment (ex: trisla-decision-engine): ' dep; restart $dep ;;
    6) health ;;
    7) audit ;;
    8) e2e ;;
    9) exit ;;
esac

read -p "Pressione ENTER para continuar..."
done
