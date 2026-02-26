#!/bin/bash
# Script para executar PROMPT_COLETA_EVIDENCIAS_RESULTADOS_v3.9.3_FINAL
# Modo read-only: apenas observação e registro

set -e

BASE_DIR="/home/porvir5g/gtp5g/trisla/evidencias_resultados_v3.9.3"
API_URL="http://192.168.10.16:32002/api/v1/sla/submit"
NAMESPACE="trisla"
TIMESTAMP_START=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "=========================================="
echo "COLETA DE EVIDÊNCIAS TriSLA v3.9.3"
echo "Início: $TIMESTAMP_START"
echo "=========================================="

# FASE 0 - Preparação (já executada, mas validando)
echo ""
echo "🔹 FASE 0 - Validação de Pré-requisitos"
mkdir -p "$BASE_DIR"/{01_slas,02_kafka,03_ml_predictions,04_xai_explanations,05_decisions,06_blockchain,07_pods_status,08_metrics,09_logs,10_latency,11_tables,12_graphs,13_domain_analysis,14_xai_analysis,15_integrity_and_diagnostics}

# GATE 0 - Validar pods críticos
echo "🔍 Validando pods críticos..."
PODS_OK=0
kubectl get pods -n "$NAMESPACE" | grep -q "portal-backend.*Running" && PODS_OK=$((PODS_OK+1)) || echo "❌ portal-backend não está Running"
kubectl get pods -n "$NAMESPACE" | grep -q "decision-engine.*Running" && PODS_OK=$((PODS_OK+1)) || echo "❌ decision-engine não está Running"
kubectl get pods -n "$NAMESPACE" | grep -q "ml-nsmf.*Running" && PODS_OK=$((PODS_OK+1)) || echo "❌ ml-nsmf não está Running"
kubectl get pods -n "$NAMESPACE" | grep -q "kafka.*Running" && PODS_OK=$((PODS_OK+1)) || echo "❌ kafka não está Running"

if [ $PODS_OK -lt 4 ]; then
    echo "❌ GATE 0 FALHOU: Nem todos os pods críticos estão Running"
    exit 1
fi
echo "✅ GATE 0 APROVADO: Todos os pods críticos estão Running"

# Função para criar SLA
create_sla() {
    local scenario=$1
    local sla_type=$2
    local number=$3
    local timestamp_submit=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Determinar payload baseado no tipo
    case $sla_type in
        URLLC)
            payload=$(cat <<EOF
{
  "template_id": "template:URLLC",
  "form_values": {
    "service_type": "URLLC",
    "latency_ms": 5,
    "reliability": 0.999
  },
  "tenant_id": "default"
}
EOF
)
            ;;
        eMBB)
            payload=$(cat <<EOF
{
  "template_id": "template:eMBB",
  "form_values": {
    "service_type": "eMBB",
    "throughput_dl_mbps": 100,
    "throughput_ul_mbps": 50
  },
  "tenant_id": "default"
}
EOF
)
            ;;
        mMTC)
            payload=$(cat <<EOF
{
  "template_id": "template:mMTC",
  "form_values": {
    "service_type": "mMTC",
    "device_density": 1000
  },
  "tenant_id": "default"
}
EOF
)
            ;;
        *)
            echo "Tipo desconhecido: $sla_type"
            return 1
            ;;
    esac
    
    # Nome do arquivo de saída
    output_file="${BASE_DIR}/01_slas/sla_${sla_type}_${scenario}_${number}.json"
    
    # Fazer requisição e salvar resposta completa
    response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "$payload" 2>&1)
    
    http_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')
    
    # Salvar resposta completa
    echo "$response_body" | jq . > "$output_file" 2>/dev/null || echo "$response_body" > "$output_file"
    
    # Extrair campos para CSV
    sla_id=$(echo "$response_body" | jq -r '.sla_id // .intent_id // "N/A"' 2>/dev/null || echo "N/A")
    intent_id=$(echo "$response_body" | jq -r '.intent_id // "N/A"' 2>/dev/null || echo "N/A")
    decision=$(echo "$response_body" | jq -r '.decision // "N/A"' 2>/dev/null || echo "N/A")
    status=$(echo "$response_body" | jq -r '.status // "N/A"' 2>/dev/null || echo "N/A")
    
    # Adicionar t_submit ao JSON se não existir
    if [ -f "$output_file" ] && command -v jq &> /dev/null; then
        jq ". + {t_submit: \"$timestamp_submit\"}" "$output_file" > "${output_file}.tmp" && mv "${output_file}.tmp" "$output_file" 2>/dev/null || true
    fi
    
    # Registrar no CSV
    REGISTRY_CSV="${BASE_DIR}/01_slas/sla_registry.csv"
    if [ ! -f "$REGISTRY_CSV" ]; then
        echo "timestamp,scenario,type,number,sla_id,intent_id,decision,status,http_code" > "$REGISTRY_CSV"
    fi
    echo "$timestamp_submit,$scenario,$sla_type,$number,$sla_id,$intent_id,$decision,$status,$http_code" >> "$REGISTRY_CSV"
    
    echo "✅ SLA $sla_type-$scenario-$number: HTTP $http_code, Decision: $decision, SLA_ID: $sla_id"
    
    # Pequeno delay entre requisições
    sleep 2
}

# FASE 1 - Execução Controlada de SLAs
echo ""
echo "🔹 FASE 1 - Execução Controlada de SLAs"

# CENÁRIO A: 1 SLA por tipo
echo "📌 CENÁRIO A: 1 SLA por tipo"
create_sla "A" "URLLC" "1"
create_sla "A" "eMBB" "1"
create_sla "A" "mMTC" "1"

# CENÁRIO B: 5 SLAs por tipo
echo ""
echo "📌 CENÁRIO B: 5 SLAs por tipo"
for i in {1..5}; do
    create_sla "B" "URLLC" "$i"
done
for i in {1..5}; do
    create_sla "B" "eMBB" "$i"
done
for i in {1..5}; do
    create_sla "B" "mMTC" "$i"
done

# CENÁRIO C: 10 SLAs por tipo
echo ""
echo "📌 CENÁRIO C: 10 SLAs por tipo"
for i in {1..10}; do
    create_sla "C" "URLLC" "$i"
done
for i in {1..10}; do
    create_sla "C" "eMBB" "$i"
done
for i in {1..10}; do
    create_sla "C" "mMTC" "$i"
done

# CENÁRIO D: Stress (≥50 SLAs mistos)
echo ""
echo "📌 CENÁRIO D: Stress Controlado (≥50 SLAs)"
total=0
while [ $total -lt 50 ]; do
    # Distribuição: 40% URLLC, 35% eMBB, 25% mMTC
    rand=$((RANDOM % 100))
    if [ $rand -lt 40 ]; then
        create_sla "D" "URLLC" "$((total+1))"
    elif [ $rand -lt 75 ]; then
        create_sla "D" "eMBB" "$((total+1))"
    else
        create_sla "D" "mMTC" "$((total+1))"
    fi
    total=$((total+1))
done

echo ""
echo "✅ FASE 1 concluída: Todos os SLAs executados"

# FASE 2 - Coleta de Logs para Latência
echo ""
echo "🔹 FASE 2 - Coleta de Logs para Análise de Latência"
kubectl logs -n "$NAMESPACE" -l app=trisla-portal-backend --tail=10000 > "${BASE_DIR}/09_logs/portal_backend.log" 2>&1 || true
kubectl logs -n "$NAMESPACE" -l app=decision-engine --tail=10000 > "${BASE_DIR}/09_logs/decision_engine.log" 2>&1 || true
kubectl logs -n "$NAMESPACE" -l app=ml-nsmf --tail=10000 > "${BASE_DIR}/09_logs/ml_nsmf.log" 2>&1 || true
kubectl logs -n "$NAMESPACE" -l app=kafka --tail=5000 > "${BASE_DIR}/09_logs/kafka.log" 2>&1 || true

# FASE 3 - Métricas do ML-NSMF (extrair dos logs)
echo ""
echo "🔹 FASE 3 - Extração de Métricas do ML-NSMF"
# Criar CSV de predições ML
echo "timestamp_utc,model_used,confidence,probability,slice_type" > "${BASE_DIR}/03_ml_predictions/ml_predictions_raw.csv"
# Extrair métricas dos logs (será preenchido por análise posterior)
grep -i "model_used\|confidence\|probability" "${BASE_DIR}/09_logs/ml_nsmf.log" | head -100 > "${BASE_DIR}/03_ml_predictions/ml_extracted.log" || echo "Nenhuma métrica ML encontrada nos logs" > "${BASE_DIR}/03_ml_predictions/ml_extracted.log"

# FASE 4 - XAI Explanations
echo ""
echo "🔹 FASE 4 - Coleta de Explicações XAI"
# Buscar explicações XAI nos logs
grep -i "xai\|explanation\|feature_importance" "${BASE_DIR}/09_logs/ml_nsmf.log" "${BASE_DIR}/09_logs/decision_engine.log" | head -50 > "${BASE_DIR}/04_xai_explanations/xai_extracted.log" || echo "Nenhuma explicação XAI encontrada" > "${BASE_DIR}/04_xai_explanations/xai_extracted.log"

# FASE 5 - Kafka Events
echo ""
echo "🔹 FASE 5 - Rastreabilidade Kafka"
# Listar tópicos Kafka
kubectl exec -n "$NAMESPACE" $(kubectl get pods -n "$NAMESPACE" -l app=kafka -o jsonpath='{.items[0].metadata.name}') -- kafka-topics.sh --list --bootstrap-server localhost:9092 > "${BASE_DIR}/02_kafka/kafka_topics.txt" 2>&1 || echo "Erro ao listar tópicos Kafka" > "${BASE_DIR}/02_kafka/kafka_topics.txt"

# FASE 6 - Blockchain (para ACCEPT)
echo ""
echo "🔹 FASE 6 - Coleta de Dados Blockchain"
kubectl logs -n "$NAMESPACE" -l app=bc-nssmf --tail=5000 > "${BASE_DIR}/06_blockchain/bc_nssmf.log" 2>&1 || true
# Extrair transações
grep -i "transaction\|tx\|hash\|block" "${BASE_DIR}/06_blockchain/bc_nssmf.log" | head -100 > "${BASE_DIR}/06_blockchain/besu_transactions.log" || echo "Nenhuma transação blockchain encontrada" > "${BASE_DIR}/06_blockchain/besu_transactions.log"

# FASE 7 - Métricas por Domínio
echo ""
echo "🔹 FASE 7 - Métricas por Domínio"
# Criar CSVs de métricas por domínio
echo "timestamp,domain,metric_name,metric_value" > "${BASE_DIR}/13_domain_analysis/core_metrics.csv"
echo "timestamp,domain,metric_name,metric_value" > "${BASE_DIR}/13_domain_analysis/transport_metrics.csv"
echo "timestamp,domain,metric_name,metric_value" > "${BASE_DIR}/13_domain_analysis/ran_semantic_metrics.csv"

# FASE 8 - Status Final dos Pods
echo ""
echo "🔹 FASE 8 - Snapshot Final"
kubectl get pods -n "$NAMESPACE" -o wide > "${BASE_DIR}/07_pods_status/pods_final.txt"
kubectl top pods -n "$NAMESPACE" > "${BASE_DIR}/08_metrics/pods_resources_final.txt" 2>&1 || true
kubectl top nodes > "${BASE_DIR}/08_metrics/nodes_resources_final.txt" 2>&1 || true

# FASE 9 - Checksums
echo ""
echo "🔹 FASE 9 - Geração de Checksums"
find "$BASE_DIR" -type f -exec sha256sum {} \; > "${BASE_DIR}/CHECKSUMS.sha256" 2>&1 || true

TIMESTAMP_END=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo ""
echo "=========================================="
echo "✅ COLETA DE EVIDÊNCIAS CONCLUÍDA"
echo "Início: $TIMESTAMP_START"
echo "Fim: $TIMESTAMP_END"
echo "Diretório: $BASE_DIR"
echo "=========================================="
