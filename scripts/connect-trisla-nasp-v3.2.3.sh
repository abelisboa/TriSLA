#!/usr/bin/env bash
set -euo pipefail

JUMP_HOST="${JUMP_HOST:-ppgca.unisinos.br}"
NASP_HOST="${NASP_HOST:-node1}"

PROM_NS_DEFAULT="monitoring"
PROM_SVC_DEFAULT="prometheus-kube-prometheus-prometheus"
PROM_REMOTE_PORT_DEFAULT="9090"
PROM_LOCAL_CANDIDATES=(9091 9092 9093)

SEM_NS_DEFAULT="trisla-nsp"
SEM_SVC_DEFAULT="sem-nsmf"
SEM_REMOTE_PORT_DEFAULT="8080"
SEM_LOCAL_CANDIDATES=(8088 8090 8092)
SEM_HEALTH_PATH="/api/v1/health"

log(){ echo -e "$1"; }
port_free(){ ! lsof -i TCP:"$1" -sTCP:LISTEN >/dev/null 2>&1; }
pick_port(){ for p in "$@"; do if port_free "$p"; then echo "$p"; return 0; fi; done; echo "$1"; }
sshq(){ ssh -q -o BatchMode=yes -J "$JUMP_HOST" "$NASP_HOST" "$@"; }

detect_port(){
  local ns="$1" svc="$2" def_port="$3"
  local line
  line=$(sshq "kubectl -n $ns get svc $svc -o jsonpath='{.spec.ports[0].port}'" 2>/dev/null || true)
  if [[ -z "$line" ]]; then
    echo "$def_port"
  else
    echo "$line"
  fi
}

start_remote_pf(){
  local ns="$1" svc="$2" rport="$3"
  local cmd="nohup kubectl -n $ns port-forward svc/$svc $rport:$rport >/dev/null 2>&1 & echo \$!"
  ssh -J "$JUMP_HOST" "$NASP_HOST" "$cmd"
}

start_local_tunnel(){
  local lport="$1" rport="$2"
  ssh -f -N -4 -o ExitOnForwardFailure=yes -J "$JUMP_HOST" "$NASP_HOST" -L "$lport:127.0.0.1:$rport"
}

wait_ready(){
  local url="$1" retries="${2:-20}"
  for i in $(seq 1 "$retries"); do
    if curl -fs "$url" >/dev/null 2>&1; then return 0; fi
    sleep 1
  done
  return 1
}

echo "======================================================"
echo "🚇  Conector TriSLA ↔ NASP v3.2.3"
echo "======================================================"

# SSH sanity
if ssh -q -o BatchMode=yes "$JUMP_HOST" exit; then
  echo "✅ SSH jump host ok."
else
  echo "❌ SSH jump host indisponível."; exit 1
fi

# PROMETHEUS
PROM_NS="${PROM_NS:-$PROM_NS_DEFAULT}"
PROM_SVC="${PROM_SVC:-$PROM_SVC_DEFAULT}"
PROM_REMOTE_PORT="$(detect_port "$PROM_NS" "$PROM_SVC" "$PROM_REMOTE_PORT_DEFAULT")"
PROM_LOCAL_PORT="$(pick_port "${PROM_LOCAL_CANDIDATES[@]}")"
echo "🧩 Prometheus: ns=$PROM_NS svc=$PROM_SVC rport=$PROM_REMOTE_PORT → local $PROM_LOCAL_PORT"

PROM_PF_PID=$(start_remote_pf "$PROM_NS" "$PROM_SVC" "$PROM_REMOTE_PORT" || true)
start_local_tunnel "$PROM_LOCAL_PORT" "$PROM_REMOTE_PORT" || true
if wait_ready "http://localhost:${PROM_LOCAL_PORT}/-/ready" 15; then
  echo "🟢 Prometheus online em http://localhost:${PROM_LOCAL_PORT}"
else
  echo "🔴 Prometheus offline (tente novamente)."
fi

# SEM-NSMF
SEM_NS="${SEM_NS:-$SEM_NS_DEFAULT}"
SEM_SVC="${SEM_SVC:-$SEM_SVC_DEFAULT}"
SEM_REMOTE_PORT="$(detect_port "$SEM_NS" "$SEM_SVC" "$SEM_REMOTE_PORT_DEFAULT")"
SEM_LOCAL_PORT="$(pick_port "${SEM_LOCAL_CANDIDATES[@]}")"
echo "🧩 SEM-NSMF: ns=$SEM_NS svc=$SEM_SVC rport=$SEM_REMOTE_PORT → local $SEM_LOCAL_PORT"

SEM_PF_PID=$(start_remote_pf "$SEM_NS" "$SEM_SVC" "$SEM_REMOTE_PORT" || true)
start_local_tunnel "$SEM_LOCAL_PORT" "$SEM_REMOTE_PORT" || true
if wait_ready "http://localhost:${SEM_LOCAL_PORT}${SEM_HEALTH_PATH}" 15; then
  echo "🟢 SEM-NSMF online em http://localhost:${SEM_LOCAL_PORT}${SEM_HEALTH_PATH}"
else
  echo "🔴 SEM-NSMF offline (tente novamente)."
fi

cat > .env.tunnels <<EOF
PROMETHEUS_URL=http://localhost:${PROM_LOCAL_PORT}
SEM_NSMF_URL=http://localhost:${SEM_LOCAL_PORT}
EOF

echo "✅ Conexões configuradas. Variáveis salvas em .env.tunnels"
