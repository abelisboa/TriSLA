#!/usr/bin/env bash

set -euo pipefail

NS=${1:-trisla}
ADAPTER_DEPLOY="trisla-nasp-adapter"
PORT_LOCAL=18085
PORT_REMOTE=8085
TS=$(date -u +%Y%m%dT%H%M%SZ)

BASE_DIR="/home/porvir5g/gtp5g/trisla"
OUT_DIR="${BASE_DIR}/evidencias_nsi_validation/nsi_validation_${TS}"

mkdir -p "$OUT_DIR"

echo "==========================================="
echo "TriSLA NSI FULL VALIDATION"
echo "Namespace : $NS"
echo "Output    : $OUT_DIR"
echo "==========================================="

echo "1️⃣ Iniciando port-forward..."
kubectl port-forward -n "$NS" deploy/"$ADAPTER_DEPLOY" ${PORT_LOCAL}:${PORT_REMOTE} > "$OUT_DIR/port_forward.log" 2>&1 &
PF_PID=$!

sleep 3

echo "2️⃣ Testando /health..."
curl -s http://127.0.0.1:${PORT_LOCAL}/health | tee "$OUT_DIR/health.json"
echo

echo "3️⃣ Enviando NSI URLLC REAL..."

NSI_ID="probe-urllc-${TS}"

curl -s -o "$OUT_DIR/instantiate_response.json" \
     -w "HTTP_STATUS:%{http_code}\n" \
     -X POST http://127.0.0.1:${PORT_LOCAL}/api/v1/nsi/instantiate \
     -H "Content-Type: application/json" \
     -d "{
        \"nsiId\": \"${NSI_ID}\",
        \"serviceProfile\": \"URLLC\",
        \"tenantId\": \"default\",
        \"sla\": { \"latency_max_ms\": 10 }
     }" \
     | tee "$OUT_DIR/http_status.txt"

echo

echo "4️⃣ Aguardando 5 segundos para reconcile..."
sleep 5

echo "5️⃣ Verificando CRD NetworkSliceInstance..."
kubectl get networksliceinstance "${NSI_ID}" -n "$NS" -o yaml > "$OUT_DIR/nsi.yaml" 2>&1 || true

echo "6️⃣ Verificando namespace isolado..."
kubectl get ns "ns-${NSI_ID}" -o yaml > "$OUT_DIR/namespace.yaml" 2>&1 || true

echo "7️⃣ Verificando ResourceQuota..."
kubectl get resourcequota -n "ns-${NSI_ID}" -o yaml > "$OUT_DIR/resourcequota.yaml" 2>&1 || true

echo "8️⃣ Coletando logs recentes do NASP Adapter..."
kubectl logs -n "$NS" deploy/"$ADAPTER_DEPLOY" --since=3m > "$OUT_DIR/adapter_logs.txt" 2>&1 || true

echo "9️⃣ Encerrando port-forward..."
kill $PF_PID 2>/dev/null || true

echo "==========================================="
echo "VALIDATION COMPLETED"
echo "NSI ID   : ${NSI_ID}"
echo "Evidence : ${OUT_DIR}"
echo "==========================================="
