#!/usr/bin/env bash
set -euo pipefail
JUMP_HOST="${JUMP_HOST:-ppgca.unisinos.br}"
NASP_HOST="${NASP_HOST:-node1}"
PROM_SVC="${PROM_SVC:-prometheus-kube-prometheus-prometheus}"
SEM_SVC="${SEM_SVC:-sem-nsmf}"

PROM_LOCAL_PORTS=(9090 9091 9092)
SEM_LOCAL_PORTS=(8080 8088 8090)
SEM_HEALTH="/api/v1/health"

log(){ echo -e "$1"; }
ssh_exec(){ ssh -o BatchMode=yes -J "$JUMP_HOST" "$NASP_HOST" "$@"; }
port_free(){ ! lsof -i :"$1" >/dev/null 2>&1; }
pick_port(){ for p in "$@"; do port_free "$p" && echo "$p" && return 0; done; echo "$1"; }
start_pf_remote(){ ssh_exec "pgrep -a kubectl | grep 'port-forward' | grep 'svc/${2} ' | awk '{print \$1}' | xargs -r kill -9 || true"; ssh_exec "nohup kubectl -n ${1} port-forward svc/${2} ${3}:${3} --address 127.0.0.1 >/tmp/${4}-pf.log 2>&1 & disown"; }
start_local_tunnel(){ fuser -k "$1"/tcp >/dev/null 2>&1 || true; ssh -f -N -L "$1:127.0.0.1:$2" -J "$JUMP_HOST" "$NASP_HOST"; }
http_ok(){ curl -m 3 -fsS "$1" >/dev/null 2>&1; }
detect_svc(){ local line ns ports port; line=$(ssh_exec "kubectl get svc -A | awk '/$1/{print \$1, \$2, \$5}' | head -n1"); [[ -z "$line" ]] && return 1; ns=$(echo "$line" | awk '{print $1}'); ports=$(echo "$line" | awk '{print $3}'); port=$(echo "$ports" | sed 's#/TCP##g' | cut -d',' -f1); echo "$ns $port"; }

log "======================================================"
log "🚇  Conector TriSLA ↔ NASP v3.2"
log "======================================================"

ssh -o BatchMode=yes -J "$JUMP_HOST" "$NASP_HOST" "hostname" >/dev/null 2>&1 || { log "❌ SSH indisponível"; exit 1; }
log "✅ SSH operacional."

read -r PROM_NS PROM_RPORT < <(detect_svc "$PROM_SVC" || echo "monitoring 9090")
PROM_LPORT=$(pick_port "${PROM_LOCAL_PORTS[@]}")
log "🧩 Prometheus: ns=${PROM_NS} porta=${PROM_RPORT} → local ${PROM_LPORT}"
start_pf_remote "$PROM_NS" "$PROM_SVC" "$PROM_RPORT" "prometheus"
start_local_tunnel "$PROM_LPORT" "$PROM_RPORT"
if http_ok "http://127.0.0.1:${PROM_LPORT}/-/ready"; then log "🟢 Prometheus online em http://localhost:${PROM_LPORT}"; else log "🔴 Prometheus não respondeu"; fi

read -r SEM_NS SEM_RPORT < <(detect_svc "$SEM_SVC" || echo "trisla-nsp 8080")
SEM_LPORT=$(pick_port "${SEM_LOCAL_PORTS[@]}")
log "🧠 SEM-NSMF: ns=${SEM_NS} porta=${SEM_RPORT} → local ${SEM_LPORT}"
start_pf_remote "$SEM_NS" "$SEM_SVC" "$SEM_RPORT" "sem-nsmf"
start_local_tunnel "$SEM_LPORT" "$SEM_RPORT"
sleep 1
if curl -m 3 -fsS "http://127.0.0.1:${SEM_LPORT}${SEM_HEALTH}" | grep -qiE "running|ok|ready|phase"; then
  log "🟢 SEM-NSMF online em http://localhost:${SEM_LPORT}${SEM_HEALTH}"
  for path in "/api/v1/jobs" "/api/v1/npl" "/api/v1/gst"; do
    if http_ok "http://127.0.0.1:${SEM_LPORT}${path}"; then log "   ✅ Endpoint OK: ${path}"; else log "   ⚠️  Endpoint indisponível: ${path}"; fi
  done
else
  log "🔴 SEM-NSMF offline (health falhou)"
fi
log "✅ Finalizado."
