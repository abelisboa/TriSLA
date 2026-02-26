#!/usr/bin/env bash
set -euo pipefail

TRISLA_NS="${TRISLA_NS:-trisla}"
MON_NS="${MON_NS:-monitoring}"
CORE_NS="${CORE_NS:-ns-1274485}"
OPEN5GS_NS="${OPEN5GS_NS:-open5gs}"

GRAFANA_SVC="${GRAFANA_SVC:-prometheus-grafana}"
GRAFANA_PF_PORT="${GRAFANA_PF_PORT:-3000}"

EVDIR_SRC="${EVDIR_SRC:-}"
if [[ -z "$EVDIR_SRC" ]]; then
  EVDIR_SRC="$(ls -dt evidencias_observability_F0_F4_* 2>/dev/null | head -n 1 || true)"
fi

UTC_NOW="$(date -u +%Y%m%dT%H%M%SZ)"
EVDIR="evidencias_trisla_dashboard_update_${UTC_NOW}"
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

is_valid_json_file() {
  local f="$1"
  [[ -s "$f" ]] || return 1
  python3 - "$f" <<'PY' >/dev/null 2>&1
import json,sys
json.load(open(sys.argv[1]))
PY
}

# Normaliza o arquivo de métricas para sempre ser JSON válido:
# - Se inválido/vazio, registra evidência e cria [] válido
normalize_metric_names_json() {
  local f="$1"
  if [[ ! -f "$f" ]]; then
    echo "[]" >"$EVDIR/metric_names_normalized.json"
    echo "MISSING_INPUT: $f" >"$EVDIR/metric_names_normalize_note.txt"
    return 0
  fi

  if is_valid_json_file "$f"; then
    cp -f "$f" "$EVDIR/metric_names_normalized.json"
    echo "OK_VALID_JSON: $f" >"$EVDIR/metric_names_normalize_note.txt"
    return 0
  fi

  # inválido: guardar conteúdo bruto (até 200 linhas) para evidência
  {
    echo "INVALID_JSON_INPUT: $f"
    echo "FILE_SIZE_BYTES: $(wc -c <"$f" 2>/dev/null || echo 0)"
    echo "HEAD(200):"
    sed -n '1,200p' "$f" 2>/dev/null || true
  } >"$EVDIR/metric_names_invalid_evidence.txt"

  # fallback válido
  echo "[]" >"$EVDIR/metric_names_normalized.json"
  echo "FALLBACK_TO_EMPTY_ARRAY" >"$EVDIR/metric_names_normalize_note.txt"
}

has_metric() {
  local name="$1"
  local f="$EVDIR/metric_names_normalized.json"
  python3 - "$f" "$name" <<'PY'
import json,sys
p=sys.argv[1]; m=sys.argv[2]
j=json.load(open(p))
data=j.get("data", j if isinstance(j,list) else [])
if isinstance(data, dict):
  data=data.get("data", [])
s=set(data if isinstance(data,list) else [])
print("YES" if m in s else "NO")
PY
}

log "Evidência base (source): ${EVDIR_SRC:-<none>}"
if [[ -n "${EVDIR_SRC:-}" && -d "$EVDIR_SRC" ]]; then
  echo "$EVDIR_SRC" >"$EVDIR/source_dir.txt"
else
  echo "NO_SOURCE_DIR" >"$EVDIR/source_dir.txt"
fi

METRICS_NAMES_IN="${EVDIR_SRC}/FASE3_prom_metric_names.json"
normalize_metric_names_json "$METRICS_NAMES_IN"

HTTP_REQ_TOTAL="NO"
HTTP_REQ_DUR="NO"
PROCESS_CPU="NO"

for cand in http_requests_total http_request_duration_seconds_sum starlette_requests_total; do
  if [[ "$(has_metric "$cand")" == "YES" ]]; then
    HTTP_REQ_TOTAL="YES"
    echo "$cand" >"$EVDIR/http_metric_detected.txt"
    break
  fi
done

for cand in http_request_duration_seconds_bucket http_request_duration_seconds_sum; do
  if [[ "$(has_metric "$cand")" == "YES" ]]; then
    HTTP_REQ_DUR="YES"
    echo "$cand" >"$EVDIR/http_latency_metric_detected.txt"
    break
  fi
done

if [[ "$(has_metric "process_cpu_seconds_total")" == "YES" ]]; then
  PROCESS_CPU="YES"
fi

log "Detect: HTTP_REQ_TOTAL=$HTTP_REQ_TOTAL HTTP_DUR=$HTTP_REQ_DUR PROCESS_CPU=$PROCESS_CPU"

start_pf
PW="$(get_pw)"
if [[ -z "$PW" ]]; then
  log "ERRO: não consegui ler admin-password do secret prometheus-grafana"
  exit 1
fi

JSON_OUT="$EVDIR/dashboard_payload.json"

cat >"$JSON_OUT" <<JSON
{
  "dashboard": {
    "uid": "trisla-observability",
    "title": "TriSLA Observability",
    "tags": ["trisla", "observability"],
    "timezone": "browser",
    "schemaVersion": 39,
    "version": 1,
    "refresh": "10s",
    "time": { "from": "now-15m", "to": "now" },
    "templating": {
      "list": [
        { "name": "namespace_trisla", "type": "constant", "query": "${TRISLA_NS}", "current": { "text": "${TRISLA_NS}", "value": "${TRISLA_NS}" } },
        { "name": "core_ns", "type": "constant", "query": "${CORE_NS}", "current": { "text": "${CORE_NS}", "value": "${CORE_NS}" } },
        { "name": "open5gs_ns", "type": "constant", "query": "${OPEN5GS_NS}", "current": { "text": "${OPEN5GS_NS}", "value": "${OPEN5GS_NS}" } }
      ]
    },
    "panels": [
      { "id": 1, "type": "stat", "title": "TriSLA Pods Ready", "gridPos": { "h": 4, "w": 6, "x": 0, "y": 0 },
        "targets": [ { "expr": "sum(kube_pod_status_ready{namespace=\\\"\$namespace_trisla\\\", condition=\\\"true\\\"})", "refId": "A" } ] },

      { "id": 2, "type": "stat", "title": "Core 5GC Ready (AMF/SMF/UPF/PCF/NRF)", "gridPos": { "h": 4, "w": 6, "x": 6, "y": 0 },
        "targets": [ { "expr": "sum(kube_pod_status_ready{namespace=\\\"\$core_ns\\\", pod=~\\\"(amf|smf|upf|pcf|nrf)-.*\\\", condition=\\\"true\\\"})", "refId": "A" } ] },

      { "id": 3, "type": "stat", "title": "Open5GS UPF Ready", "gridPos": { "h": 4, "w": 6, "x": 12, "y": 0 },
        "targets": [ { "expr": "sum(kube_pod_status_ready{namespace=\\\"\$open5gs_ns\\\", pod=~\\\"open5gs-upf-.*\\\", condition=\\\"true\\\"})", "refId": "A" } ] },

      { "id": 4, "type": "stat", "title": "Tempo Distributor: traces/batch (count)", "gridPos": { "h": 4, "w": 6, "x": 18, "y": 0 },
        "targets": [ { "expr": "tempo_distributor_traces_per_batch_count", "refId": "A" } ] },

      { "id": 5, "type": "timeseries", "title": "UPF Free5GC Throughput (RX Mbps)", "gridPos": { "h": 8, "w": 12, "x": 0, "y": 4 },
        "targets": [ { "expr": "8/1e6 * sum by (pod) (rate(container_network_receive_bytes_total{namespace=\\\"\$core_ns\\\", pod=~\\\"upf-.*\\\"}[1m]))", "refId": "A" } ] },

      { "id": 6, "type": "timeseries", "title": "UPF Free5GC Throughput (TX Mbps)", "gridPos": { "h": 8, "w": 12, "x": 12, "y": 4 },
        "targets": [ { "expr": "8/1e6 * sum by (pod) (rate(container_network_transmit_bytes_total{namespace=\\\"\$core_ns\\\", pod=~\\\"upf-.*\\\"}[1m]))", "refId": "A" } ] },

      { "id": 7, "type": "timeseries", "title": "UPF Free5GC CPU (cores)", "gridPos": { "h": 8, "w": 12, "x": 0, "y": 12 },
        "targets": [ { "expr": "sum by (pod) (rate(container_cpu_usage_seconds_total{namespace=\\\"\$core_ns\\\", pod=~\\\"upf-.*\\\", container!=\\\"\\\", image!=\\\"\\\"}[5m]))", "refId": "A" } ] },

      { "id": 8, "type": "timeseries", "title": "UPF Free5GC Memory (MiB)", "gridPos": { "h": 8, "w": 12, "x": 12, "y": 12 },
        "targets": [ { "expr": "sum by (pod) (container_memory_working_set_bytes{namespace=\\\"\$core_ns\\\", pod=~\\\"upf-.*\\\", container!=\\\"\\\", image!=\\\"\\\"}) / 1024 / 1024", "refId": "A" } ] },

      { "id": 9, "type": "timeseries", "title": "TriSLA CPU (cores) — all pods", "gridPos": { "h": 8, "w": 12, "x": 0, "y": 20 },
        "targets": [ { "expr": "sum by (pod) (rate(container_cpu_usage_seconds_total{namespace=\\\"\$namespace_trisla\\\", container!=\\\"\\\", image!=\\\"\\\"}[5m]))", "refId": "A" } ] },

      { "id": 10, "type": "timeseries", "title": "TriSLA Memory (MiB) — all pods", "gridPos": { "h": 8, "w": 12, "x": 12, "y": 20 },
        "targets": [ { "expr": "sum by (pod) (container_memory_working_set_bytes{namespace=\\\"\$namespace_trisla\\\", container!=\\\"\\\", image!=\\\"\\\"}) / 1024 / 1024", "refId": "A" } ] }
    ]
  },
  "overwrite": true
}
JSON

# HTTP panels só se detectado
if [[ "$HTTP_REQ_TOTAL" == "YES" || "$HTTP_REQ_DUR" == "YES" ]]; then
  log "Inserindo painéis HTTP detectados"
  python3 - "$JSON_OUT" "$HTTP_REQ_TOTAL" "$HTTP_REQ_DUR" <<'PY'
import json,sys
p=sys.argv[1]
has_total=sys.argv[2]=="YES"
has_dur=sys.argv[3]=="YES"
j=json.load(open(p))
panels=j["dashboard"]["panels"]
y=28
pid=100
if has_total:
  panels.append({
    "id": pid, "type":"timeseries", "title":"TriSLA HTTP requests/sec (global)",
    "gridPos":{"h":8,"w":12,"x":0,"y":y},
    "targets":[{"expr":"sum(rate(http_requests_total[1m]))","refId":"A"}]
  })
  pid+=1
if has_dur:
  panels.append({
    "id": pid, "type":"timeseries", "title":"TriSLA HTTP p95 latency (s)",
    "gridPos":{"h":8,"w":12,"x":12,"y":y},
    "targets":[{"expr":"histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))","refId":"A"}]
  })
open(p,"w").write(json.dumps(j))
PY
fi

log "Aplicando dashboard via API"
curl -sS -u "admin:${PW}" -H 'Content-Type: application/json' \
  -X POST "http://127.0.0.1:${GRAFANA_PF_PORT}/api/dashboards/db" \
  --data @"$JSON_OUT" >"$EVDIR/api_apply_response.json" || true

log "OK: evidências em $EVDIR"
echo "$EVDIR"
