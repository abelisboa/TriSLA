#!/bin/bash
# =============================================================
# TriSLA NASP — PortGuard Utility (AutoWatch Daemon Version)
# Autor: Abel Lisboa
# Última atualização: $(date +"%F")
# =============================================================
# Garante que o TriSLA Portal (API e UI) permaneça acessível.
# Inclui modo contínuo (--watch) que repara automaticamente
# falhas de port-forward e monitora o endpoint de saúde.
# =============================================================

set -e
NAMESPACE="trisla"
SERVICE="trisla-portal"
API_PORT=30800
API_TARGET=8000
UI_PORT=30173
UI_TARGET=5173
NODE_IP=$(hostname -I | awk '{print $1}')
LOG_DIR="/var/log/trisla-portguard"
CHECK_INTERVAL=30  # segundos entre verificações
mkdir -p "$LOG_DIR"

# =============================================================
# Funções auxiliares
# =============================================================

check_and_kill_port() {
  local port=$1
  local pids
  pids=$(sudo ss -lntp | grep ":$port" | awk '{print $NF}' | grep -oP 'pid=\K[0-9]+' || true)
  if [[ -n "$pids" ]]; then
    echo "⚠️  Porta $port em uso por PID(s): $pids — encerrando..."
    for pid in $pids; do
      sudo kill -9 "$pid" 2>/dev/null || true
    done
  else
    echo "✅ Porta $port livre."
  fi
}

start_port_forward() {
  local port=$1
  local target=$2
  local name=$3
  local log_file="$LOG_DIR/${name}_$(date +%H%M%S).log"
  echo "🔄 Iniciando port-forward para $name ($port → $target)..."
  nohup kubectl port-forward -n "$NAMESPACE" svc/"$SERVICE" "$port":"$target" --address 0.0.0.0 >"$log_file" 2>&1 &
  sleep 3
}

test_api_health() {
  local response
  response=$(curl -s http://localhost:$API_PORT/api/v1/health || true)
  if echo "$response" | grep -q "TriSLA Portal API running"; then
    echo "✅ API OK — $response"
    return 0
  else
    echo "❌ API falhou — resposta: $response"
    return 1
  fi
}

# =============================================================
# Execução principal
# =============================================================

echo "🚀 TriSLA PortGuard — NASP Auto Recovery Daemon"
echo "------------------------------------------------------------"

# 1️⃣ Checa dependências
for cmd in kubectl ss curl; do
  if ! command -v $cmd >/dev/null 2>&1; then
    echo "❌ Dependência ausente: $cmd"
    exit 1
  fi
done

# 2️⃣ Remove forwards antigos
check_and_kill_port $API_PORT
check_and_kill_port $UI_PORT

# 3️⃣ Inicia novos port-forwards
start_port_forward $API_PORT $API_TARGET "api"
start_port_forward $UI_PORT $UI_TARGET "ui"

# 4️⃣ Testa primeira resposta
test_api_health || {
  echo "⚠️ Primeira tentativa falhou — aguardando 10s e tentando novamente..."
  sleep 10
  test_api_health || echo "⚠️ API ainda não respondeu, prosseguindo com monitoramento..."
}

# 5️⃣ Mostra status inicial
echo "------------------------------------------------------------"
echo "🌐 TriSLA Portal ativo:"
echo "   → API: http://$NODE_IP:$API_PORT/api/v1/health"
echo "   → UI : http://$NODE_IP:$UI_PORT/"
echo "📋 Logs em: $LOG_DIR/"
echo "------------------------------------------------------------"

# 6️⃣ Modo contínuo (--watch)
if [[ "$1" == "--watch" ]]; then
  echo "👁️  Modo de monitoramento contínuo ativado (intervalo: ${CHECK_INTERVAL}s)"
  while true; do
    sleep $CHECK_INTERVAL

    # Se port-forward morreu, reinicia
    if ! sudo ss -lntp | grep -q ":$API_PORT"; then
      echo "⚠️ Port-forward API caiu — reiniciando..."
      check_and_kill_port $API_PORT
      start_port_forward $API_PORT $API_TARGET "api"
    fi

    if ! sudo ss -lntp | grep -q ":$UI_PORT"; then
      echo "⚠️ Port-forward UI caiu — reiniciando..."
      check_and_kill_port $UI_PORT
      start_port_forward $UI_PORT $UI_TARGET "ui"
    fi

    # Testa o endpoint
    if ! test_api_health; then
      echo "⚠️ API sem resposta — tentando recuperação..."
      check_and_kill_port $API_PORT
      start_port_forward $API_PORT $API_TARGET "api"
      sleep 5
      test_api_health || echo "❌ API ainda indisponível após tentativa de recuperação."
    fi
  done
fi

echo "🎯 PortGuard concluído com sucesso — ambiente NASP estável!"

