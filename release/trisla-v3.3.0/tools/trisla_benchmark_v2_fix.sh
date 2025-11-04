#!/bin/bash
# =============================================================
# TriSLA Benchmark v2 (FIX) — Stable Metrics Collector
# Autor: Abel Lisboa
# =============================================================

set -euo pipefail

NAMESPACE_MON="monitoring"
RESULTS_DIR="/var/log/trisla-benchmark"
EXPORT_DIR="$HOME/trisla-results"

mkdir -p "$RESULTS_DIR" "$EXPORT_DIR"

PROM_SVC="prometheus-kube-prometheus-prometheus"
PROM_LOCAL_PORT=30900
PROM_URL_INTERNAL="http://prometheus.monitoring.svc:9090/api/v1/query"
PROM_URL_EXTERNAL="http://localhost:${PROM_LOCAL_PORT}/api/v1/query"

LOG_FILE="$RESULTS_DIR/benchmark_fix.log"
echo "[$(date '+%F %T')] Starting TriSLA Benchmark v2 (FIX)..." | tee -a "$LOG_FILE"

# ------------------------------------------------------------
# 1️⃣ Detectar acesso Prometheus
# ------------------------------------------------------------
if kubectl run tmp-prom-test --rm -i -n "$NAMESPACE_MON" \
    --restart=Never --image=curlimages/curl -- curl -s "$PROM_URL_INTERNAL" >/dev/null 2>&1; then
  PROM_URL="$PROM_URL_INTERNAL"
  echo "[OK] Prometheus interno acessível" | tee -a "$LOG_FILE"
else
  echo "[WARN] Acesso interno falhou, iniciando port-forward..." | tee -a "$LOG_FILE"
  sudo pkill -f "port-forward.*${PROM_SVC}" || true
  nohup kubectl port-forward -n "$NAMESPACE_MON" svc/$PROM_SVC ${PROM_LOCAL_PORT}:9090 --address 0.0.0.0 >/dev/null 2>&1 &
  sleep 5
  if curl -s "$PROM_URL_EXTERNAL" >/dev/null 2>&1; then
    PROM_URL="$PROM_URL_EXTERNAL"
    echo "[OK] Port-forward ativo: $PROM_URL" | tee -a "$LOG_FILE"
  else
    echo "[ERROR] Prometheus inacessível. Abortando." | tee -a "$LOG_FILE"
    exit 1
  fi
fi

# ------------------------------------------------------------
# 2️⃣ Funções auxiliares
# ------------------------------------------------------------
query_metric() {
  local metric="$1"
  local value
  value=$(curl -s "${PROM_URL}?query=avg_over_time(${metric}[60s])" | jq -r '.data.result[0].value[1]' 2>/dev/null)
  echo "$value" | grep -Eo '[0-9]+(\.[0-9]+)?' || echo "0"
}

calc_avg() {
  local -a vals=("${@:2}")
  local sum=0 count=0
  for v in "${vals[@]}"; do
    [[ -z "$v" || "$v" == "null" || "$v" == "NaN" ]] && continue
    sum=$(echo "$sum + $v" | bc -l 2>/dev/null || echo "$sum")
    ((count++))
  done
  [[ $count -gt 0 ]] && echo "scale=4; $sum / $count" | bc -l 2>/dev/null || echo "0"
}

# ------------------------------------------------------------
# 3️⃣ Coletar métricas
# ------------------------------------------------------------
echo "------------------------------------------------------------"
echo "Executando benchmark — URLLC | eMBB | mMTC"
echo "------------------------------------------------------------"

urlc_latency=$(query_metric "trisla_latency_ms")
urlc_jitter=$(query_metric "trisla_jitter_ms")
urlc_loss=$(query_metric "trisla_packet_loss")

embb_thr=$(query_metric "trisla_throughput_mbps")
embb_bw=$(query_metric "trisla_bandwidth_util")
embb_retx=$(query_metric "trisla_tcp_retx")

mmtc_conn=$(query_metric "trisla_conn_density")
mmtc_rate=$(query_metric "trisla_msg_rate")
mmtc_cpu=$(query_metric "trisla_cpu_load")

avg_urlc=$(calc_avg "URLLC" "$urlc_latency" "$urlc_jitter" "$urlc_loss")
avg_embb=$(calc_avg "eMBB" "$embb_thr" "$embb_bw" "$embb_retx")
avg_mmtc=$(calc_avg "mMTC" "$mmtc_conn" "$mmtc_rate" "$mmtc_cpu")

# ------------------------------------------------------------
# 4️⃣ Exportar resultados
# ------------------------------------------------------------
timestamp=$(date +%F_%H-%M-%S)
json_file="$EXPORT_DIR/benchmark_${timestamp}.json"
tex_file="$EXPORT_DIR/benchmark_${timestamp}.tex"

cat > "$json_file" <<EOF2
{
  "timestamp": "$timestamp",
  "urlcc": { "latency_ms": "$urlc_latency", "jitter_ms": "$urlc_jitter", "packet_loss": "$urlc_loss", "avg": "$avg_urlc" },
  "embb":  { "throughput_mbps": "$embb_thr", "bandwidth_util": "$embb_bw", "tcp_retx": "$embb_retx", "avg": "$avg_embb" },
  "mmtc":  { "conn_density": "$mmtc_conn", "msg_rate": "$mmtc_rate", "cpu_load": "$mmtc_cpu", "avg": "$avg_mmtc" }
}
EOF2

cat > "$tex_file" <<EOF3
\\begin{table}[H]
\\centering
\\caption{Resultados do Benchmark TriSLA — $(date +%d/%m/%Y)}
\\label{tab:trisla-benchmark}
\\begin{tabular}{|l|c|c|c|c|}
\\hline
\\textbf{Slice} & \\textbf{Métrica 1} & \\textbf{Métrica 2} & \\textbf{Métrica 3} & \\textbf{Média Geral} \\\\ \\hline
URLLC & ${urlc_latency} ms & jitter ${urlc_jitter} ms & perda ${urlc_loss} \\% & ${avg_urlc} \\\\ \\hline
eMBB & ${embb_thr} Mbps & uso ${embb_bw} \\% & retx ${embb_retx} \\% & ${avg_embb} \\\\ \\hline
mMTC & dens ${mmtc_conn} & msgs ${mmtc_rate}/s & CPU ${mmtc_cpu} \\% & ${avg_mmtc} \\\\ \\hline
\\end{tabular}
\\end{table}
EOF3

echo "------------------------------------------------------------"
echo "✅ Benchmark concluído com sucesso!"
echo "📄 JSON: $json_file"
echo "📘 LaTeX: $tex_file"
echo "------------------------------------------------------------"
