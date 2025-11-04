#!/usr/bin/env bash
set -euo pipefail
JUMP_HOST="ppgca.unisinos.br"
NASP_HOST="node1"
PROM_SVC="prometheus-kube-prometheus-prometheus"
SEM_SVC="sem-nsmf"

PROM_LOCAL_PORTS=(9090 9091 9092)
SEM_LOCAL_PORTS=(8080 8088 8090)
SEM_HEALTH="/api/v1/health"

log(){ echo -e "$1"; }
ssh_exec(){ ssh -o BatchMode=yes -J "$JUMP_HOST" "$NASP_HOST" "$@"; }
port_free(){ ! lsof -i :"$1" >/dev/null 2>&1; }
pick_port(){ for p in "$@"; do port_free "$p" && echo "$p" && return 0; done; echo "$1"; }

detect_svc(){
  local line ns ports port
  line=$(ssh_exec "kubectl get svc -A | awk '/$1/{print \$1, \$2, \$5}' | head -n1")
  [[ -z "$line" ]] && return 1
  ns=$(echo "$line" | awk '{print $1}')
  ports=$(echo "$line" | awk '{print $3}')
  port=$(echo "$ports" | sed 's#/TCP##g' | cut -d',' -f1)
  [[ -z "$port" || "$port" == "<none>" ]] && port=""
  echo "$ns ${port:-none}"
}

log "======================================================"
log "🚇  Conector TriSLA ↔ NASP v3.2.1"
log "======================================================"

ssh -o BatchMode=yes -J "$JUMP_HOST" "$NASP_HOST" "hostname" >/dev/null 2>&1 || { log "❌ SSH indisponível"; exit 1; }
log "✅ SSH operacional."

read -r PROM_NS PROM_RPORT < <(detect_svc "$PROM_SVC" || echo "monitoring none")
if [[ "$PROM_RPORT" == "none" || -z "$PROM_RPORT" ]]; then
  log "⚠️  Porta Prometheus desconhecida, usando padrão 9090"
  PROM_RPORT=9090
fi
PROM_LPORT=$(pick_port "${PROM_LOCAL_PORTS[@]}")
log "🧩 Prometheus: ns=${PROM_NS} porta=${PROM_RPORT} → local ${PROM_LPORT}"
ssh_exec "pgrep -a kubectl | grep 'port-forward' | grep 'svc/${PROM_SVC} ' | awk '{print \$1}' | xargs -r kill -9 || true"
ssh_exec "nohup kubectl -n ${PROM_NS} port-forward svc/${PROM_SVC} ${PROM_RPORT}:${PROM_RPORT} --address 127.0.0.1 >/tmp/prometheus-pf.log 2>&1 & disown"
ssh -f -N -L ${PROM_LPORT}:127.0.0.1:${PROM_RPORT} -J "$JUMP_HOST" "$NASP_HOST" || true
if curl -m 3 -fsS "http://127.0.0.1:${PROM_LPORT}/-/ready" >/dev/null; then log "🟢 Prometheus online em http://localhost:${PROM_LPORT}"; else log "🔴 Prometheus não respondeu"; fi

read -r SEM_NS SEM_RPORT < <(detect_svc "$SEM_SVC" || echo "trisla-nsp none")
if [[ "$SEM_RPORT" == "none" || -z "$SEM_RPORT" ]]; then
  log "⚠️  Porta SEM-NSMF desconhecida, usando padrão 8080"
  SEM_RPORT=8080
fi
SEM_LPORT=$(pick_port "${SEM_LOCAL_PORTS[@]}")
log "🧠 SEM-NSMF: ns=${SEM_NS} porta=${SEM_RPORT} → local ${SEM_LPORT}"
ssh_exec "pgrep -a kubectl | grep 'port-forward' | grep 'svc/${SEM_SVC} ' | awk '{print \$1}' | xargs -r kill -9 || true"
ssh_exec "nohup kubectl -n ${SEM_NS} port-forward svc/${SEM_SVC} ${SEM_RPORT}:${SEM_RPORT} --address 127.0.0.1 >/tmp/sem-nsmf-pf.log 2>&1 & disown"
ssh -f -N -L ${SEM_LPORT}:127.0.0.1:${SEM_RPORT} -J "$JUMP_HOST" "$NASP_HOST" || true
sleep 2
if curl -m 3 -fsS "http://127.0.0.1:${SEM_LPORT}${SEM_HEALTH}" | grep -qiE "running|ok|ready|phase"; then
  log "🟢 SEM-NSMF online em http://localhost:${SEM_LPORT}${SEM_HEALTH}"
else
  log "🔴 SEM-NSMF offline (falha no health check)"
fi

log "✅ Finalizado."
