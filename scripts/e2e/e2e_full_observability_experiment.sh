#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="trisla"
CORE_NS="ns-1274485"
RAN_NS="ueransim"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
BASE_DIR="/home/porvir5g/gtp5g/trisla/evidencias_e2e_full/${TIMESTAMP}"

mkdir -p "${BASE_DIR}"/{baseline,post,blockchain,sla_metrics,summary}

echo "=============================================="
echo "TriSLA FULL E2E OBSERVABILITY EXPERIMENT"
echo "Evidence: ${BASE_DIR}"
echo "=============================================="

########################################
# FASE 1 — BASELINE
########################################

echo "[1] Capturando baseline CORE..."
kubectl top pod -n ${CORE_NS} > ${BASE_DIR}/baseline/core_top.txt || true
kubectl get pods -n ${CORE_NS} -o wide > ${BASE_DIR}/baseline/core_pods.txt

echo "[1] Capturando baseline RAN..."
kubectl get pods -n ${RAN_NS} > ${BASE_DIR}/baseline/ran_pods.txt

echo "[1] Capturando baseline Transporte (ping)..."
kubectl run -n ${NAMESPACE} rtt-baseline --rm -i --restart=Never --image=busybox \
  -- sh -c "ping -c 5 trisla-nasp-adapter" \
  > ${BASE_DIR}/baseline/rtt.txt || true

########################################
# FASE 2 — SUBMIT SLA
########################################

echo "[2] Submetendo SLA..."

kubectl run -n ${NAMESPACE} sla-submit --rm -i --restart=Never --image=curlimages/curl:8.6.0 -- \
  sh -c "curl -s -X POST http://trisla-portal-backend:8001/api/v1/sla/submit \
  -H 'Content-Type: application/json' \
  -d '{\"template_id\":\"default\",\"form_values\":{\"service_type\":\"urllc\"},\"tenant_id\":\"default\"}'" \
  > ${BASE_DIR}/submit_response.json

cat ${BASE_DIR}/submit_response.json

DECISION=$(jq -r '.decision' ${BASE_DIR}/submit_response.json)
SLA_ID=$(jq -r '.sla_id' ${BASE_DIR}/submit_response.json)
TX_HASH=$(jq -r '.tx_hash' ${BASE_DIR}/submit_response.json)
BLOCK_NUMBER=$(jq -r '.block_number' ${BASE_DIR}/submit_response.json)

if [[ "$DECISION" != "ACCEPT" ]]; then
  echo "❌ SLA não foi ACCEPT"
  exit 1
fi

########################################
# FASE 3 — STABILIZATION
########################################

sleep 20

########################################
# FASE 4 — POST SNAPSHOT
########################################

echo "[4] Capturando pós-SLA CORE..."
kubectl top pod -n ${CORE_NS} > ${BASE_DIR}/post/core_top.txt || true
kubectl get pods -n ${CORE_NS} -o wide > ${BASE_DIR}/post/core_pods.txt

echo "[4] Capturando pós-SLA RAN..."
kubectl get pods -n ${RAN_NS} > ${BASE_DIR}/post/ran_pods.txt

########################################
# FASE 5 — SLA METRICS
########################################

kubectl run -n ${NAMESPACE} sla-metrics --rm -i --restart=Never --image=curlimages/curl:8.6.0 -- \
  sh -c "curl -s http://trisla-portal-backend:8001/api/v1/sla/metrics/${SLA_ID}" \
  > ${BASE_DIR}/sla_metrics/metrics.json

########################################
# FASE 6 — SUMMARY
########################################

jq -n \
  --arg decision "$DECISION" \
  --arg sla_id "$SLA_ID" \
  --arg tx "$TX_HASH" \
  --arg block "$BLOCK_NUMBER" \
  '{decision:$decision, sla_id:$sla_id, tx_hash:$tx, block_number:$block}' \
  > ${BASE_DIR}/summary/experiment_summary.json

echo "=============================================="
echo "✅ EXPERIMENTO CONCLUÍDO"
echo "SLA_ID: $SLA_ID"
echo "TX: $TX_HASH"
echo "Block: $BLOCK_NUMBER"
echo "Evidence: ${BASE_DIR}"
echo "=============================================="
