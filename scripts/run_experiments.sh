#!/bin/bash
################################################################################
# WU-005 — Script de Execução dos Experimentos TriSLA@NASP
# Autor: Abel José Rodrigues Lisboa
# Data: 2025-10-17
# Ambiente: NASP@UNISINOS
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="trisla-nsp"
BASE_DIR="/home/porvir5g/gtp5g/trisla-nsp"
EXPERIMENTS_DIR="${BASE_DIR}/experiments"
RESULTS_DIR="${EXPERIMENTS_DIR}/results"
LOG_FILE="${RESULTS_DIR}/experiments.log"

# Experiment parameters
URLLC_DURATION=1800    # 30 minutes
EMBB_DURATION=1800     # 30 minutes
MMTC_DURATION=1800     # 30 minutes
TOTAL_DURATION=5400    # 90 minutes

# Scenario configurations
declare -A SCENARIOS=(
    ["urllc"]="1"
    ["embb"]="10"
    ["mmtc"]="100"
)

declare -A SCENARIO_NAMES=(
    ["urllc"]="URLLC - Telemedicina"
    ["embb"]="eMBB - Streaming 4K"
    ["mmtc"]="mMTC - IoT Massivo"
)

################################################################################
# Functions
################################################################################

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1" | tee -a "$LOG_FILE"
}

log_scenario() {
    echo -e "${PURPLE}[$(date +'%Y-%m-%d %H:%M:%S')] SCENARIO:${NC} $1" | tee -a "$LOG_FILE"
}

check_prerequisites() {
    log "Checking prerequisites for WU-005 experiments..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Please install kubectl."
        exit 1
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster."
        exit 1
    fi
    
    # Check namespace
    if ! kubectl get namespace ${NAMESPACE} &> /dev/null; then
        log_error "Namespace ${NAMESPACE} not found."
        exit 1
    fi
    
    # Check TriSLA pods
    local trisla_pods=$(kubectl get pods -n ${NAMESPACE} --no-headers 2>/dev/null | wc -l)
    if [ "$trisla_pods" -lt 5 ]; then
        log_error "Not all TriSLA pods are running. Found: $trisla_pods"
        exit 1
    fi
    
    log "Prerequisites OK ✓"
}

create_directories() {
    log "Creating experiment directories..."
    
    mkdir -p "${EXPERIMENTS_DIR}/scenarios/{urllc,embb,mmtc}"
    mkdir -p "${EXPERIMENTS_DIR}/data/{intents,predictions,contracts}"
    mkdir -p "${RESULTS_DIR}/{metrics,logs,contracts,reports}"
    
    log "Directories created ✓"
}

initialize_monitoring() {
    log "Initializing monitoring and metrics collection..."
    
    # Start background metrics collection
    nohup ./scripts/collect_metrics.sh > "${RESULTS_DIR}/metrics_collection.log" 2>&1 &
    local metrics_pid=$!
    echo $metrics_pid > "${RESULTS_DIR}/metrics_pid.txt"
    
    # Initialize experiment tracking
    cat > "${RESULTS_DIR}/experiment_config.json" <<EOF
{
  "start_time": "$(date -Iseconds)",
  "namespace": "${NAMESPACE}",
  "scenarios": {
    "urllc": {"duration": ${URLLC_DURATION}, "requests_per_second": 1},
    "embb": {"duration": ${EMBB_DURATION}, "requests_per_second": 10},
    "mmtc": {"duration": ${MMTC_DURATION}, "requests_per_second": 100}
  },
  "total_duration": ${TOTAL_DURATION}
}
EOF
    
    log "Monitoring initialized ✓"
}

run_scenario() {
    local scenario=$1
    local duration=$2
    local rps=$3
    local scenario_name="${SCENARIO_NAMES[$scenario]}"
    
    log_scenario "Starting ${scenario_name} (${duration}s, ${rps} req/s)"
    
    local start_time=$(date +%s)
    local end_time=$((start_time + duration))
    local request_count=0
    
    # Create scenario-specific log
    local scenario_log="${RESULTS_DIR}/logs/${scenario}_scenario.log"
    echo "=== ${scenario_name} Experiment ===" > "$scenario_log"
    echo "Start: $(date)" >> "$scenario_log"
    echo "Duration: ${duration}s" >> "$scenario_log"
    echo "RPS: ${rps}" >> "$scenario_log"
    echo "" >> "$scenario_log"
    
    # Generate intent based on scenario
    local intent=""
    case $scenario in
        "urllc")
            intent='{"request":"cirurgia remota","sla_requirements":{"latency_max":"10ms","reliability_min":"99.999%"}}'
            ;;
        "embb")
            intent='{"request":"streaming 4k","sla_requirements":{"throughput_min":"1000Mbps","latency_max":"50ms"}}'
            ;;
        "mmtc")
            intent='{"request":"iot massivo","sla_requirements":{"device_count":"10000","latency_max":"100ms"}}'
            ;;
    esac
    
    # Run scenario
    while [ $(date +%s) -lt $end_time ]; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        local remaining=$((end_time - current_time))
        
        # Send request
        local response=$(kubectl exec -n ${NAMESPACE} deploy/trisla-semantic-layer -- \
            curl -s -X POST http://localhost:8080/intent \
            -H "Content-Type: application/json" \
            -d "$intent" 2>/dev/null || echo "ERROR")
        
        ((request_count++))
        
        # Log progress every 60 seconds
        if [ $((elapsed % 60)) -eq 0 ]; then
            log_info "${scenario_name}: ${elapsed}s elapsed, ${remaining}s remaining, ${request_count} requests sent"
            echo "[${elapsed}s] Request ${request_count}: ${response}" >> "$scenario_log"
        fi
        
        # Sleep to maintain RPS
        sleep $((1 / rps))
    done
    
    # Finalize scenario
    local total_time=$(date +%s)
    local actual_duration=$((total_time - start_time))
    
    echo "End: $(date)" >> "$scenario_log"
    echo "Total requests: ${request_count}" >> "$scenario_log"
    echo "Actual duration: ${actual_duration}s" >> "$scenario_log"
    echo "Average RPS: $(echo "scale=2; $request_count / $actual_duration" | bc)" >> "$scenario_log"
    
    log_scenario "Completed ${scenario_name}: ${request_count} requests in ${actual_duration}s"
    
    # Save scenario results
    cat > "${RESULTS_DIR}/scenarios/${scenario}_results.json" <<EOF
{
  "scenario": "${scenario}",
  "name": "${scenario_name}",
  "start_time": "${start_time}",
  "end_time": "${total_time}",
  "duration": ${actual_duration},
  "requests_sent": ${request_count},
  "target_rps": ${rps},
  "actual_rps": $(echo "scale=2; $request_count / $actual_duration" | bc)
}
EOF
}

collect_final_metrics() {
    log "Collecting final metrics and logs..."
    
    # Stop metrics collection
    if [ -f "${RESULTS_DIR}/metrics_pid.txt" ]; then
        local metrics_pid=$(cat "${RESULTS_DIR}/metrics_pid.txt")
        kill $metrics_pid 2>/dev/null || true
        rm -f "${RESULTS_DIR}/metrics_pid.txt"
    fi
    
    # Collect pod logs
    for pod in $(kubectl get pods -n ${NAMESPACE} -o name); do
        local pod_name=$(basename $pod)
        kubectl logs -n ${NAMESPACE} $pod_name > "${RESULTS_DIR}/logs/${pod_name}.log" 2>&1
    done
    
    # Collect system metrics
    kubectl top pods -n ${NAMESPACE} > "${RESULTS_DIR}/metrics/pod_metrics.txt"
    kubectl top nodes > "${RESULTS_DIR}/metrics/node_metrics.txt"
    
    # Collect service status
    kubectl get all -n ${NAMESPACE} -o wide > "${RESULTS_DIR}/metrics/k8s_resources.txt"
    
    # Export Prometheus metrics (if accessible)
    if kubectl get svc -n monitoring prometheus-kube-prometheus-prometheus &> /dev/null; then
        kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090 &
        local prometheus_pid=$!
        sleep 5
        
        # Export key metrics
        curl -s "http://localhost:9090/api/v1/query?query=rate(http_requests_total{namespace=\"${NAMESPACE}\"}[5m])" > "${RESULTS_DIR}/metrics/prometheus_requests.json"
        curl -s "http://localhost:9090/api/v1/query?query=histogram_quantile(0.99,sum(rate(http_request_duration_seconds_bucket{namespace=\"${NAMESPACE}\"}[5m]))by(le))" > "${RESULTS_DIR}/metrics/prometheus_latency.json"
        
        kill $prometheus_pid 2>/dev/null || true
    fi
    
    log "Final metrics collected ✓"
}

generate_report() {
    log "Generating experimental report..."
    
    # Create summary report
    cat > "${RESULTS_DIR}/reports/experimental_summary.md" <<EOF
# WU-005 — Relatório de Avaliação Experimental TriSLA@NASP

**Data:** $(date)
**Responsável:** Abel José Rodrigues Lisboa
**Ambiente:** NASP@UNISINOS

## Resumo da Execução

- **Duração total:** ${TOTAL_DURATION} segundos (90 minutos)
- **Cenários executados:** 3 (URLLC, eMBB, mMTC)
- **Namespace:** ${NAMESPACE}
- **Pods monitorados:** $(kubectl get pods -n ${NAMESPACE} --no-headers | wc -l)

## Cenários Executados

EOF

    # Add scenario results to report
    for scenario in urllc embb mmtc; do
        if [ -f "${RESULTS_DIR}/scenarios/${scenario}_results.json" ]; then
            local name=$(jq -r '.name' "${RESULTS_DIR}/scenarios/${scenario}_results.json")
            local requests=$(jq -r '.requests_sent' "${RESULTS_DIR}/scenarios/${scenario}_results.json")
            local duration=$(jq -r '.duration' "${RESULTS_DIR}/scenarios/${scenario}_results.json")
            local rps=$(jq -r '.actual_rps' "${RESULTS_DIR}/scenarios/${scenario}_results.json")
            
            cat >> "${RESULTS_DIR}/reports/experimental_summary.md" <<EOF
### ${name}
- **Requisições enviadas:** ${requests}
- **Duração:** ${duration} segundos
- **RPS médio:** ${rps}

EOF
        fi
    done
    
    cat >> "${RESULTS_DIR}/reports/experimental_summary.md" <<EOF
## Evidências Coletadas

- Logs de cenários: \`results/logs/\`
- Métricas do sistema: \`results/metrics/\`
- Configuração do experimento: \`results/experiment_config.json\`
- Log principal: \`results/experiments.log\`

## Próximos Passos

1. Analisar métricas coletadas
2. Validar hipóteses H1, H2, H3
3. Gerar relatório final de conformidade SLA
4. Documentar evidências para dissertação

EOF
    
    log "Report generated ✓"
}

cleanup() {
    log "Cleaning up background processes..."
    
    # Kill any remaining background processes
    if [ -f "${RESULTS_DIR}/metrics_pid.txt" ]; then
        local metrics_pid=$(cat "${RESULTS_DIR}/metrics_pid.txt")
        kill $metrics_pid 2>/dev/null || true
        rm -f "${RESULTS_DIR}/metrics_pid.txt"
    fi
    
    # Clean up port forwards
    pkill -f "kubectl port-forward" 2>/dev/null || true
    
    log "Cleanup completed ✓"
}

################################################################################
# Main Execution
################################################################################

main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                                                                ║"
    echo "║       WU-005 — Avaliação Experimental TriSLA@NASP              ║"
    echo "║                                                                ║"
    echo "║  Executando 3 cenários: URLLC, eMBB, mMTC                     ║"
    echo "║  Duração total: 90 minutos                                     ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Initialize log
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "=== WU-005 Experimental Evaluation Log ===" > "$LOG_FILE"
    echo "Date: $(date)" >> "$LOG_FILE"
    echo "Namespace: ${NAMESPACE}" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    # Set up cleanup trap
    trap cleanup EXIT
    
    # Execute experiment phases
    check_prerequisites
    create_directories
    initialize_monitoring
    
    # Run scenarios
    run_scenario "urllc" $URLLC_DURATION 1
    run_scenario "embb" $EMBB_DURATION 10
    run_scenario "mmtc" $MMTC_DURATION 100
    
    collect_final_metrics
    generate_report
    
    echo ""
    log "═══════════════════════════════════════════════════════════════"
    log "  WU-005 Experimental Evaluation completed!"
    log "═══════════════════════════════════════════════════════════════"
    log "  Results directory: ${RESULTS_DIR}"
    log "  Main log: ${LOG_FILE}"
    log "  Summary report: ${RESULTS_DIR}/reports/experimental_summary.md"
    log "═══════════════════════════════════════════════════════════════"
    echo ""
}

# Run main function
main "$@"
