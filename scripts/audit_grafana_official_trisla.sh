#!/usr/bin/env bash
set -euo pipefail

MON_NS="${MON_NS:-monitoring}"
GRAFANA_SVC="${GRAFANA_SVC:-prometheus-grafana}"
GRAFANA_PF_PORT="${GRAFANA_PF_PORT:-3000}"

UTC_NOW="$(date -u +%Y%m%dT%H%M%SZ)"
EVDIR="evidencias_grafana_official_audit_${UTC_NOW}"
mkdir -p "$EVDIR"

log(){ echo "[$(date -u +%H:%M:%SZ)] $*"; }

port_in_use() {
  local p="$1"
  if command -v ss >/dev/null 2>&1; then
    ss -lnt "( sport = :$p )" 2>/dev/null | grep -q ":$p" && return 0 || return 1
  else
    return 1
  fi
}

start_pf() {
  if port_in_use "$GRAFANA_PF_PORT"; then
    log "PF SKIP: porta ${GRAFANA_PF_PORT} já em uso."
    echo "PF_SKIP port=${GRAFANA_PF_PORT}" >"$EVDIR/PF_STATUS.txt"
    return 0
  fi
  kubectl -n "$MON_NS" port-forward "svc/$GRAFANA_SVC" "${GRAFANA_PF_PORT}:80" >/dev/null 2>&1 &
  echo $! >"$EVDIR/PF_PID.txt"
  sleep 0.8
  log "PF_OK: svc/$GRAFANA_SVC -> localhost:${GRAFANA_PF_PORT}"
  echo "PF_OK svc/$GRAFANA_SVC port=${GRAFANA_PF_PORT}" >"$EVDIR/PF_STATUS.txt"
}

cleanup() {
  if [[ -f "$EVDIR/PF_PID.txt" ]]; then
    kill "$(cat "$EVDIR/PF_PID.txt")" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

get_pw() {
  kubectl -n "$MON_NS" get secret prometheus-grafana -o jsonpath='{.data.admin-password}' 2>/dev/null | base64 -d 2>/dev/null || true
}

log "Inventário base"
{
  echo "UTC: $UTC_NOW"
  echo "MON_NS: $MON_NS"
  echo "GRAFANA_SVC: $GRAFANA_SVC"
  echo
  echo "== helm list =="
  helm list -A 2>/dev/null | egrep -i 'prometheus|grafana|kube-prometheus|tempo' || true
  echo
  echo "== svc grafana =="
  kubectl -n "$MON_NS" get svc "$GRAFANA_SVC" -o wide || true
  echo
  echo "== endpoints grafana =="
  kubectl -n "$MON_NS" get endpoints "$GRAFANA_SVC" -o wide || true
} >"$EVDIR/INVENTORY.txt"

start_pf

PW="$(get_pw)"
if [[ -z "$PW" ]]; then
  log "ERRO: não consegui ler admin-password do secret prometheus-grafana"
  exit 1
fi

log "Coletando datasources, dashboards e health"
curl -sS -u "admin:${PW}" "http://127.0.0.1:${GRAFANA_PF_PORT}/api/health" >"$EVDIR/api_health.json" || true
curl -sS -u "admin:${PW}" "http://127.0.0.1:${GRAFANA_PF_PORT}/api/datasources" >"$EVDIR/api_datasources.json" || true
curl -sS -u "admin:${PW}" "http://127.0.0.1:${GRAFANA_PF_PORT}/api/search?query=TriSLA" >"$EVDIR/api_search_trisla.json" || true
curl -sS -u "admin:${PW}" "http://127.0.0.1:${GRAFANA_PF_PORT}/api/dashboards/uid/trisla-observability" >"$EVDIR/api_dashboard_trisla_observability.json" || true

log "OK: evidências em $EVDIR"
echo "$EVDIR"
