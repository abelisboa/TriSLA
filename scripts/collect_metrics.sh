#!/bin/bash
################################################################################
# WU-005 — Script de Coleta de Métricas TriSLA@NASP
# Autor: Abel José Rodrigues Lisboa
# Data: 2025-10-17
# Ambiente: NASP@UNISINOS
################################################################################

# Configuration
NAMESPACE="trisla-nsp"
BASE_DIR="/home/porvir5g/gtp5g/trisla-nsp"
RESULTS_DIR="${BASE_DIR}/experiments/results"
METRICS_DIR="${RESULTS_DIR}/metrics"
INTERVAL=10  # seconds

# Create metrics directory
mkdir -p "$METRICS_DIR"

# Initialize metrics files
echo "timestamp,pod_name,cpu_cores,memory_mib" > "${METRICS_DIR}/pod_metrics.csv"
echo "timestamp,node_name,cpu_percent,memory_percent" > "${METRICS_DIR}/node_metrics.csv"
echo "timestamp,scenario,request_id,response_time_ms,status" > "${METRICS_DIR}/request_metrics.csv"

log_metrics() {
    local timestamp=$(date -Iseconds)
    
    # Collect pod metrics
    kubectl top pods -n ${NAMESPACE} --no-headers | while read line; do
        local pod_name=$(echo $line | awk '{print $1}')
        local cpu=$(echo $line | awk '{print $2}' | sed 's/m//')
        local memory=$(echo $line | awk '{print $3}' | sed 's/Mi//')
        echo "${timestamp},${pod_name},${cpu},${memory}" >> "${METRICS_DIR}/pod_metrics.csv"
    done
    
    # Collect node metrics
    kubectl top nodes --no-headers | while read line; do
        local node_name=$(echo $line | awk '{print $1}')
        local cpu_percent=$(echo $line | awk '{print $2}' | sed 's/%//')
        local memory_percent=$(echo $line | awk '{print $4}' | sed 's/%//')
        echo "${timestamp},${node_name},${cpu_percent},${memory_percent}" >> "${METRICS_DIR}/node_metrics.csv"
    done
}

# Main collection loop
while true; do
    log_metrics
    sleep $INTERVAL
done
