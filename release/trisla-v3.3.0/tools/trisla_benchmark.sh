#!/bin/bash
# =============================================================
# TriSLA Benchmark Automation Script
# Autor: Abel Lisboa
# Data: $(date +"%F %T")
# =============================================================

set -e

NAMESPACE_MON="monitoring"
NAMESPACE_TRI="trisla-nsp"
RESULTS_DIR="/var/log/trisla-benchmark"
EXPORT_DIR="$HOME/trisla-results"

mkdir -p "$RESULTS_DIR" "$EXPORT_DIR"

PROM_URL="http://prometheus.monitoring.svc:9090/api/v1/query"
MONITOR_POD=$(kubectl get pod -n $NAMESPACE_TRI -l app=trisla-monitoring-layer -o jsonpath='{.items[0].metadata.name}')

echo "🚀 TriSLA Benchmark — URLLC | eMBB | mMTC"
echo "------------------------------------------------------------"

function query_metric() {
  local metric=$1
  local label=$2
  echo "📡 Coletando métrica: $metric"
  kubectl -n $NAMESPACE_TRI exec -i "$MONITOR_POD" -- \
    curl -s "${PROM_URL}?query=avg_over_time(${metric}[60s])" | jq -r '.data.result[0].value[1]' || echo "0"
}

function calc_stats() {
  local metric_name=$1
  local values=("$@")
  unset values[0]
  local sum=0 count=0
  for v in "${values[@]}"; do
    [[ -z "$v" ]] && continue
    sum=$(echo "$sum + $v" | bc -l)
    ((count++))
  done
  local avg=$(echo "scale=4; $sum / $count" | bc -l)
  echo "$avg"
}

# 1️⃣ URLLC — Latência
urlc_latency=$(query_metric "trisla_latency_ms")
urlc_jitter=$(query_metric "trisla_jitter_ms")
urlc_loss=$(query_metric "trisla_packet_loss")

# 2️⃣ eMBB — Vazão
embb_throughput=$(query_metric "trisla_throughput_mbps")
embb_bandwidth=$(query_metric "trisla_bandwidth_util")
embb_retx=$(query_metric "trisla_tcp_retx")

# 3️⃣ mMTC — Densidade
mmtc_conn=$(query_metric "trisla_conn_density")
mmtc_rate=$(query_metric "trisla_msg_rate")
mmtc_cpu=$(query_metric "trisla_cpu_load")

# 🧮 Estatísticas
urlc_avg=$(calc_stats "URLLC" "$urlc_latency" "$urlc_jitter" "$urlc_loss")
embb_avg=$(calc_stats "eMBB" "$embb_throughput" "$embb_bandwidth" "$embb_retx")
mmtc_avg=$(calc_stats "mMTC" "$mmtc_conn" "$mmtc_rate" "$mmtc_cpu")

timestamp=$(date +%F_%H-%M-%S)
json_file="$EXPORT_DIR/benchmark_${timestamp}.json"
tex_file="$EXPORT_DIR/benchmark_${timestamp}.tex"

cat > "$json_file" <<EOF
{
  "timestamp": "$timestamp",
  "urlcc": {
    "latency_ms": "$urlc_latency",
    "jitter_ms": "$urlc_jitter",
    "packet_loss": "$urlc_loss",
    "avg": "$urlc_avg"
  },
  "embb": {
    "throughput_mbps": "$embb_throughput",
    "bandwidth_util": "$embb_bandwidth",
    "tcp_retx": "$embb_retx",
    "avg": "$embb_avg"
  },
  "mmtc": {
    "conn_density": "$mmtc_conn",
    "msg_rate": "$mmtc_rate",
    "cpu_load": "$mmtc_cpu",
    "avg": "$mmtc_avg"
  }
}
EOF

cat > "$tex_file" <<EOF
\\begin{table}[H]
\\centering
\\caption{Resultados do Benchmark TriSLA — $(date +%d/%m/%Y)}
\\label{tab:trisla-benchmark}
\\begin{tabular}{|l|c|c|c|c|}
\\hline
\\textbf{Slice} & \\textbf{Métrica 1} & \\textbf{Métrica 2} & \\textbf{Métrica 3} & \\textbf{Média Geral} \\\\ \\hline
URLLC & ${urlc_latency} ms & jitter ${urlc_jitter} ms & perda ${urlc_loss} \\% & ${urlc_avg} \\\\ \\hline
eMBB & ${embb_throughput} Mbps & uso ${embb_bandwidth} \\% & retx ${embb_retx} \\% & ${embb_avg} \\\\ \\hline
mMTC & dens ${mmtc_conn} & msgs ${mmtc_rate}/s & CPU ${mmtc_cpu} \\% & ${mmtc_avg} \\\\ \\hline
\\end{tabular}
\\end{table}
EOF

echo "------------------------------------------------------------"
echo "✅ Benchmark concluído!"
echo "📄 JSON: $json_file"
echo "📘 LaTeX: $tex_file"
echo "------------------------------------------------------------"

#  Log persistente
echo "$(date +"%F %T") — Benchmark concluído com sucesso" | sudo tee -a "$RESULTS_DIR/history.log" > /dev/null
