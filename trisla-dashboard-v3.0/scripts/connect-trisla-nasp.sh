#!/bin/bash
# ======================================================
# TriSLA / NASP - Conector resiliente Prometheus + SEM-NSMF
# Autor: Abel Lisboa
# Data: 2025-11-01
# ======================================================

set -euo pipefail

JUMP_HOST="porvir5g@ppgca.unisinos.br"
NASP_NODE="porvir5g@node1"
NAMESPACE_MON="monitoring"
NAMESPACE_SEM="trisla"
PROM_SERVICE="prometheus-kube-prometheus-prometheus"
PROM_PORT=9090
SEM_PORT=8000
SEM_SVC="sem-nsmf"
LOG_DIR="/tmp"
PROM_LOG="$LOG_DIR/port-forward-prometheus.log"
SEM_LOG="$LOG_DIR/port-forward-sem-nsmf.log"
CHECK_INTERVAL=20 # segundos entre verificações

# ------------------------------------------------------
banner() {
  echo "======================================================"
  echo "🚇  Conector TriSLA ↔ NASP (Prometheus + SEM-NSMF)"
  echo "======================================================"
}
# ------------------------------------------------------
test_ssh() {
  echo "🔍 Verificando conexão SSH via jump host..."
  if ! ssh -q -J "$JUMP_HOST" "$NASP_NODE" "hostname" >/dev/null 2>&1; then
    echo "❌ Falha: não foi possível conectar a $NASP_NODE via $JUMP_HOST"
    exit 1
  fi
  echo "✅ SSH operacional."
}
# ------------------------------------------------------
start_remote_forward() {
  local ns=$1 svc=$2 port=$3 log=$4
  echo "🌐 Iniciando port-forward remoto de $svc (porta $port)..."
  ssh -f -J "$JUMP_HOST" "$NASP_NODE" \
    "nohup kubectl -n $ns port-forward svc/$svc $port:$port --address 127.0.0.1 >$log 2>&1 &"
}
# ------------------------------------------------------
start_local_tunnel() {
  local port=$1
  echo "🔁 Criando túnel local → remoto na porta $port..."
  # Se porta já estiver em uso, libera
  if lsof -i :$port >/dev/null 2>&1; then
    fuser -k ${port}/tcp || true
    sleep 1
  fi
  ssh -f -N -L $port:localhost:$port -J "$JUMP_HOST" "$NASP_NODE"
}
# ------------------------------------------------------
check_endpoint() {
  local name=$1 url=$2
  if curl -s --max-time 3 "$url" | grep -qi "ready\|ok"; then
    echo "🟢 $name está online ($url)"
    return 0
  else
    echo "🔴 $name offline ($url)"
    return 1
  fi
}
# ------------------------------------------------------
maintain_connection() {
  while true; do
    echo "---------------------------------------------"
    echo "🕒 $(date '+%Y-%m-%d %H:%M:%S') — verificando conexões..."
    local restart=false

    # Testa Prometheus
    if ! check_endpoint "Prometheus" "http://localhost:$PROM_PORT/-/ready"; then
      echo "⚙️ Reiniciando Prometheus tunnel..."
      restart=true
      ssh -J "$JUMP_HOST" "$NASP_NODE" "pkill -f 'kubectl.*$PROM_SERVICE' || true"
      start_remote_forward "$NAMESPACE_MON" "$PROM_SERVICE" "$PROM_PORT" "$PROM_LOG"
      start_local_tunnel "$PROM_PORT"
    fi

    # Testa SEM-NSMF
    if ! check_endpoint "SEM-NSMF" "http://localhost:$SEM_PORT/health"; then
      echo "⚙️ Reiniciando SEM-NSMF tunnel..."
      restart=true
      ssh -J "$JUMP_HOST" "$NASP_NODE" "pkill -f 'kubectl.*$SEM_SVC' || true"
      start_remote_forward "$NAMESPACE_SEM" "$SEM_SVC" "$SEM_PORT" "$SEM_LOG"
      start_local_tunnel "$SEM_PORT"
    fi

    if [ "$restart" = true ]; then
      echo "🔁 Túnel(s) restaurado(s) com sucesso."
    else
      echo "✅ Ambos serviços estáveis."
    fi

    echo "⏳ Nova checagem em $CHECK_INTERVAL s..."
    sleep $CHECK_INTERVAL
  done
}
# ------------------------------------------------------
main() {
  banner
  test_ssh

  echo "🧩 Verificando serviços no cluster..."
  ssh -J "$JUMP_HOST" "$NASP_NODE" "kubectl -n $NAMESPACE_MON get svc $PROM_SERVICE >/dev/null 2>&1" \
    && echo "✅ Prometheus encontrado." || echo "⚠️ Prometheus não encontrado."
  ssh -J "$JUMP_HOST" "$NASP_NODE" "kubectl -n $NAMESPACE_SEM get svc $SEM_SVC >/dev/null 2>&1" \
    && echo "✅ SEM-NSMF encontrado." || echo "⚠️ SEM-NSMF não encontrado."

  # Inicia forwards e túneis
  start_remote_forward "$NAMESPACE_MON" "$PROM_SERVICE" "$PROM_PORT" "$PROM_LOG"
  start_remote_forward "$NAMESPACE_SEM" "$SEM_SVC" "$SEM_PORT" "$SEM_LOG"
  start_local_tunnel "$PROM_PORT"
  start_local_tunnel "$SEM_PORT"

  echo "⌛ Aguardando inicialização dos túneis..."
  sleep 5

  check_endpoint "Prometheus" "http://localhost:$PROM_PORT/-/ready"
  check_endpoint "SEM-NSMF" "http://localhost:$SEM_PORT/health"

  echo "🚀 Conexão inicial estabelecida."
  echo "   Prometheus → http://localhost:$PROM_PORT"
  echo "   SEM-NSMF    → http://localhost:$SEM_PORT"
  echo "---------------------------------------------"
  echo "🔄 Iniciando monitoramento contínuo..."
  maintain_connection
}
# ------------------------------------------------------
main
