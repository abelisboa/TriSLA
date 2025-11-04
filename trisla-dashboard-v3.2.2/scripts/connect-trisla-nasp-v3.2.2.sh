#!/usr/bin/env bash
set -eo pipefail

JUMP_HOST="ppgca.unisinos.br"
NASP_HOST="node1"
PROM_SVC="prometheus-kube-prometheus-prometheus"
SEM_SVC="sem-nsmf"

PROM_LOCAL_PORTS=(9090 9091 9092)
SEM_LOCAL_PORTS=(8080 8088 8090)
SEM_HEALTH="/api/v1/health"

log(){ echo -e "$1"; }
ssh_exec(){ ssh -o BatchMode=yes -J "$JUMP_HOST" "$NASP_HOST" "$@"; }
port_free(){ local p=${1:-0}; ! lsof -i :"$p" >/dev/null 2>&1; }
pick_port(){ for p in "$@"; do port_free "$p" && echo "$p" && return 0; done; echo "${1:-8080}"; }

detect_svc() {
  local svc=${1:-none}
  [[ "$svc" == "none" ]] && return 1
  local line ns ports port
  line=$(ssh_exec "kubectl get svc -A | awk '/${svc}/{print \$1, \$2, \$5}' | head -n1")
  [[ -z "$line" ]] && return 1
  ns=$(echo "$line" | awk '{print $1}')
  ports=$(echo "$line" | awk '{print $3}')
  port=$(echo "$ports" | sed 's#/TCP##g' | cut -d',' -f1)
  [[ -z "$port" || "$port" == "<none>" || "$port" == "<pending>" ]] && port=""
  echo "$ns ${port:-none}"
}

log "======================================================"
log "🚇  Conector TriSLA ↔ NASP v3.2.2"
log "======================================================"

# Verifica SSH
if ssh -q -o BatchMode=yes "$JUMP_HOST" exit; then
  log "✅ SSH operacional."
else
  log "❌ SSH indisponível"
  exit 1
fi

# Detecta Prometheus
IFS=' ' read -r PROM_NS PROM_PORT <<< "$(detect_svc "$PROM_SVC" || echo 'monitoring 9090')"
[[ "$PROM_PORT" == "none" || -z "$PROM_PORT" ]] && PROM_PORT=9090
PROM_LOCAL=$(pick_port "${PROM_LOCAL_PORTS[@]}")
log "🧩 Prometheus: ns=${PROM_NS:-monitoring} porta=${PROM_PORT} → local ${PROM_LOCAL}"
ssh -f -N -J "$JUMP_HOST" "$NASP_HOST" -L "${PROM_LOCAL}:127.0.0.1:${PROM_PORT}" || true

# Detecta SEM-NSMF
IFS=' ' read -r SEM_NS SEM_PORT <<< "$(detect_svc "$SEM_SVC" || echo 'trisla-nsp 8080')"
[[ "$SEM_PORT" == "none" || -z "$SEM_PORT" ]] && SEM_PORT=8080
SEM_LOCAL=$(pick_port "${SEM_LOCAL_PORTS[@]}")
log "🧩 SEM-NSMF: ns=${SEM_NS:-trisla-nsp} porta=${SEM_PORT} → local ${SEM_LOCAL}"
ssh -f -N -J "$JUMP_HOST" "$NASP_HOST" -L "${SEM_LOCAL}:127.0.0.1:${SEM_PORT}" || true

sleep 3

# Testa endpoints
if curl -fs "http://localhost:${PROM_LOCAL}/-/ready" >/dev/null; then
  log "🟢 Prometheus online em http://localhost:${PROM_LOCAL}"
else
  log "🔴 Prometheus offline"
fi

if curl -fs "http://localhost:${SEM_LOCAL}${SEM_HEALTH}" >/dev/null; then
  log "🟢 SEM-NSMF online em http://localhost:${SEM_LOCAL}${SEM_HEALTH}"
else
  log "🔴 SEM-NSMF offline"
fi

log "✅ Conexão configurada com sucesso."
