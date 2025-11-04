#!/bin/bash
# ===========================================================
# 📊 Script de Coleta de Métricas do Prometheus - TriSLA
# Coleta métricas conforme os KPIs definidos na WU-005
# ===========================================================

PROMETHEUS_URL="${PROMETHEUS_URL:-http://localhost:9090}"
OUTPUT_DIR="${OUTPUT_DIR:-$(pwd)/docs/evidencias/WU-005_avaliacao}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
NAMESPACE="${NAMESPACE:-trisla-nsp}"

mkdir -p "$OUTPUT_DIR"

echo "==============================================="
echo "📊 Coleta de Métricas Prometheus - TriSLA"
echo "==============================================="
echo "Prometheus URL: $PROMETHEUS_URL"
echo "Namespace: $NAMESPACE"
echo "Timestamp: $TIMESTAMP"
echo ""

# Verificar se Prometheus está acessível
echo "🔍 Verificando conectividade com Prometheus..."
health_check=$(curl -s "$PROMETHEUS_URL/-/healthy" --max-time 10)
if [ $? -ne 0 ]; then
    echo "⚠️ Aviso: Prometheus pode não estar acessível em $PROMETHEUS_URL"
    echo "   Verifique se o túnel SSH está ativo ou configure PROMETHEUS_URL"
fi

# Função para executar query Prometheus
prometheus_query() {
    local query=$1
    local output_file=$2
    
    response=$(curl -s -G "$PROMETHEUS_URL/api/v1/query" \
        --data-urlencode "query=$query" \
        --max-time 30)
    
    if [ $? -eq 0 ]; then
        echo "$response" | jq . > "$output_file" 2>/dev/null || echo "$response" > "$output_file"
        echo "✅ Query executada: $(basename $output_file)"
        return 0
    else
        echo "❌ Erro ao executar query: $(basename $output_file)"
        return 1
    fi
}

# Função para executar query range (para séries temporais)
prometheus_query_range() {
    local query=$1
    local start_time=$2
    local end_time=$3
    local step=${4:-15s}
    local output_file=$5
    
    response=$(curl -s -G "$PROMETHEUS_URL/api/v1/query_range" \
        --data-urlencode "query=$query" \
        --data-urlencode "start=$start_time" \
        --data-urlencode "end=$end_time" \
        --data-urlencode "step=$step" \
        --max-time 60)
    
    if [ $? -eq 0 ]; then
        echo "$response" | jq . > "$output_file" 2>/dev/null || echo "$response" > "$output_file"
        echo "✅ Query range executada: $(basename $output_file)"
        return 0
    else
        echo "❌ Erro ao executar query range: $(basename $output_file)"
        return 1
    fi
}

echo "==============================================="
echo "🔍 Coletando Métricas de Recursos"
echo "==============================================="
echo ""

# 1. CPU Usage por pod
echo "1️⃣ CPU Usage (rate por 1 minuto)"
prometheus_query \
    "rate(container_cpu_usage_seconds_total{namespace=\"$NAMESPACE\"}[1m])" \
    "$OUTPUT_DIR/prometheus_cpu_usage_${TIMESTAMP}.json"

# 2. Memory Usage por pod
echo "2️⃣ Memory Usage"
prometheus_query \
    "container_memory_usage_bytes{namespace=\"$NAMESPACE\"}" \
    "$OUTPUT_DIR/prometheus_memory_usage_${TIMESTAMP}.json"

# 3. Latência p99 (HTTP requests)
echo "3️⃣ Latência p99 (HTTP requests)"
prometheus_query \
    "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{namespace=\"$NAMESPACE\"}[5m])) by (le, pod))" \
    "$OUTPUT_DIR/prometheus_latency_p99_${TIMESTAMP}.json"

# 4. Latência p90
echo "4️⃣ Latência p90"
prometheus_query \
    "histogram_quantile(0.90, sum(rate(http_request_duration_seconds_bucket{namespace=\"$NAMESPACE\"}[5m])) by (le, pod))" \
    "$OUTPUT_DIR/prometheus_latency_p90_${TIMESTAMP}.json"

# 5. Latência p50 (mediana)
echo "5️⃣ Latência p50 (mediana)"
prometheus_query \
    "histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket{namespace=\"$NAMESPACE\"}[5m])) by (le, pod))" \
    "$OUTPUT_DIR/prometheus_latency_p50_${TIMESTAMP}.json"

# 6. Taxa de erros HTTP 5xx
echo "6️⃣ Taxa de Erros HTTP (5xx)"
prometheus_query \
    "rate(http_requests_total{namespace=\"$NAMESPACE\",status=~\"5..\"}[5m])" \
    "$OUTPUT_DIR/prometheus_http_errors_${TIMESTAMP}.json"

# 7. Taxa total de requisições HTTP
echo "7️⃣ Taxa Total de Requisições HTTP"
prometheus_query \
    "rate(http_requests_total{namespace=\"$NAMESPACE\"}[5m])" \
    "$OUTPUT_DIR/prometheus_http_total_${TIMESTAMP}.json"

# 8. Jitter (se disponível)
echo "8️⃣ Jitter (variação de latência)"
prometheus_query \
    "histogram_stddev(http_request_duration_seconds{namespace=\"$NAMESPACE\"})" \
    "$OUTPUT_DIR/prometheus_jitter_${TIMESTAMP}.json" || echo "   ⚠️ Métrica de jitter pode não estar disponível"

# 9. Throughput (se disponível)
echo "9️⃣ Throughput"
prometheus_query \
    "rate(container_network_receive_bytes_total{namespace=\"$NAMESPACE\"}[5m]) + rate(container_network_transmit_bytes_total{namespace=\"$NAMESPACE\"}[5m])" \
    "$OUTPUT_DIR/prometheus_throughput_${TIMESTAMP}.json" || echo "   ⚠️ Métrica de throughput pode não estar disponível"

# 10. Restarts de pods
echo "🔟 Restarts de Pods"
prometheus_query \
    "kube_pod_container_status_restarts_total{namespace=\"$NAMESPACE\"}" \
    "$OUTPUT_DIR/prometheus_pod_restarts_${TIMESTAMP}.json"

# 11. Pod status (Ready/NotReady)
echo "1️⃣1️⃣ Status dos Pods (Ready)"
prometheus_query \
    "kube_pod_status_ready{namespace=\"$NAMESPACE\",condition=\"true\"}" \
    "$OUTPUT_DIR/prometheus_pod_ready_${TIMESTAMP}.json"

# 12. CPU e Memory requests/limits
echo "1️⃣2️⃣ CPU Requests e Limits"
prometheus_query \
    "kube_pod_container_resource_requests{namespace=\"$NAMESPACE\",resource=\"cpu\"}" \
    "$OUTPUT_DIR/prometheus_cpu_requests_${TIMESTAMP}.json"

prometheus_query \
    "kube_pod_container_resource_limits{namespace=\"$NAMESPACE\",resource=\"cpu\"}" \
    "$OUTPUT_DIR/prometheus_cpu_limits_${TIMESTAMP}.json"

prometheus_query \
    "kube_pod_container_resource_requests{namespace=\"$NAMESPACE\",resource=\"memory\"}" \
    "$OUTPUT_DIR/prometheus_memory_requests_${TIMESTAMP}.json"

prometheus_query \
    "kube_pod_container_resource_limits{namespace=\"$NAMESPACE\",resource=\"memory\"}" \
    "$OUTPUT_DIR/prometheus_memory_limits_${TIMESTAMP}.json"

echo ""
echo "==============================================="
echo "📈 Coletando Séries Temporais (últimos 30 min)"
echo "==============================================="
echo ""

# Calcular timestamps (últimos 30 minutos)
end_time=$(date +%s)
start_time=$((end_time - 1800))  # 30 minutos atrás

# CPU ao longo do tempo
echo "📊 CPU Usage (série temporal)"
prometheus_query_range \
    "rate(container_cpu_usage_seconds_total{namespace=\"$NAMESPACE\"}[1m])" \
    "$start_time" \
    "$end_time" \
    "15s" \
    "$OUTPUT_DIR/prometheus_cpu_timeseries_${TIMESTAMP}.json"

# Memory ao longo do tempo
echo "📊 Memory Usage (série temporal)"
prometheus_query_range \
    "container_memory_usage_bytes{namespace=\"$NAMESPACE\"}" \
    "$start_time" \
    "$end_time" \
    "15s" \
    "$OUTPUT_DIR/prometheus_memory_timeseries_${TIMESTAMP}.json"

# Latência ao longo do tempo
echo "📊 Latência p99 (série temporal)"
prometheus_query_range \
    "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{namespace=\"$NAMESPACE\"}[5m])) by (le, pod))" \
    "$start_time" \
    "$end_time" \
    "15s" \
    "$OUTPUT_DIR/prometheus_latency_timeseries_${TIMESTAMP}.json"

echo ""
echo "==============================================="
echo "📋 Consolidando Métricas"
echo "==============================================="
echo ""

# Criar arquivo consolidado
consolidated_file="$OUTPUT_DIR/prometheus_metrics_consolidated_${TIMESTAMP}.txt"
cat > "$consolidated_file" << EOF
===============================================
MÉTRICAS PROMETHEUS CONSOLIDADAS - TriSLA
===============================================
Data: $(date)
Prometheus URL: $PROMETHEUS_URL
Namespace: $NAMESPACE
Timestamp: $TIMESTAMP

MÉTRICAS COLETADAS:
-------------------
1. CPU Usage: prometheus_cpu_usage_${TIMESTAMP}.json
2. Memory Usage: prometheus_memory_usage_${TIMESTAMP}.json
3. Latência p99: prometheus_latency_p99_${TIMESTAMP}.json
4. Latência p90: prometheus_latency_p90_${TIMESTAMP}.json
5. Latência p50: prometheus_latency_p50_${TIMESTAMP}.json
6. Taxa de Erros HTTP (5xx): prometheus_http_errors_${TIMESTAMP}.json
7. Taxa Total Requisições: prometheus_http_total_${TIMESTAMP}.json
8. Jitter: prometheus_jitter_${TIMESTAMP}.json
9. Throughput: prometheus_throughput_${TIMESTAMP}.json
10. Restarts de Pods: prometheus_pod_restarts_${TIMESTAMP}.json
11. Status Pods (Ready): prometheus_pod_ready_${TIMESTAMP}.json
12. CPU Requests/Limits: prometheus_cpu_requests_${TIMESTAMP}.json, prometheus_cpu_limits_${TIMESTAMP}.json
13. Memory Requests/Limits: prometheus_memory_requests_${TIMESTAMP}.json, prometheus_memory_limits_${TIMESTAMP}.json

SÉRIES TEMPORAIS (últimos 30 minutos):
---------------------------------------
1. CPU Usage: prometheus_cpu_timeseries_${TIMESTAMP}.json
2. Memory Usage: prometheus_memory_timeseries_${TIMESTAMP}.json
3. Latência p99: prometheus_latency_timeseries_${TIMESTAMP}.json

ARQUIVOS GERADOS:
-----------------
$(ls -lh "$OUTPUT_DIR"/prometheus_*_${TIMESTAMP}* 2>/dev/null | awk '{print $9, "(" $5 ")"}' || echo "Nenhum arquivo encontrado")

===============================================
EOF

cat "$consolidated_file"

echo ""
echo "✅ Coleta de métricas concluída!"
echo "📁 Evidências salvas em: $OUTPUT_DIR"
echo ""
echo "💡 Dica: Use 'jq' para analisar os arquivos JSON:"
echo "   jq '.data.result[] | select(.metric.pod==\"sem-nsmf\")' $OUTPUT_DIR/prometheus_cpu_usage_${TIMESTAMP}.json"
echo ""





