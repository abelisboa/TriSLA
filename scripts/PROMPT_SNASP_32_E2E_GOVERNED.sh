#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "PROMPT_SNASP_32 — E2E Deterministic Admission Test"
echo "=================================================="

BASE="/home/porvir5g/gtp5g/trisla"
PORTAL_URL="http://192.168.10.15:32002/api/v1/sla/submit"
STATUS_URL="http://192.168.10.15:32002/api/v1/sla/status"
EVID="$BASE/evidencias_nasp/32_e2e_deterministic"
RUNBOOK="$BASE/docs/TRISLA_MASTER_RUNBOOK.md"
TS=$(date -u +"%Y%m%dT%H%M%SZ")

mkdir -p "$EVID"

echo "Timestamp: $TS" | tee "$EVID/00_metadata.txt"
echo "Hostname: $(hostname)" | tee -a "$EVID/00_metadata.txt"

echo "--------------------------------------------------"
echo "FASE 0 — Gate Operacional"
echo "--------------------------------------------------"

kubectl get pods -n trisla | tee "$EVID/01_pods.txt"

echo "--------------------------------------------------"
echo "FASE 1 — Coleta RTT Real (Transporte)"
echo "--------------------------------------------------"

kubectl port-forward -n trisla svc/trisla-nasp-adapter 8085:8085 >/dev/null 2>&1 &
PF_PID=$!
sleep 2

RTT=$(curl -s http://127.0.0.1:8085/api/v1/metrics/multidomain | jq -r '.transport.rtt_p95_ms')

kill $PF_PID || true

echo "RTT_REAL_MS=$RTT" | tee "$EVID/02_rtt_real.txt"

if [[ "$RTT" == "null" ]]; then
  echo "ABORT: RTT não disponível"
  exit 1
fi

LOW_LAT=$(echo "$RTT - 2" | bc)
HIGH_LAT=$(echo "$RTT + 10" | bc)

echo "LOW_LAT=$LOW_LAT" | tee -a "$EVID/02_rtt_real.txt"
echo "HIGH_LAT=$HIGH_LAT" | tee -a "$EVID/02_rtt_real.txt"

echo "--------------------------------------------------"
echo "FASE 2 — Teste URLLC (latência menor que RTT)"
echo "Esperado: FAIL"
echo "--------------------------------------------------"

RESP1=$(curl -s -X POST "$PORTAL_URL" \
  -H "Content-Type: application/json" \
  -d "{
        \"slice_type\": \"URLLC\",
        \"sla_requirements\": {
          \"latency\": { \"max_ms\": $LOW_LAT }
        }
      }")

echo "$RESP1" | tee "$EVID/03_submit_urllc_low.json"

DEC1=$(echo "$RESP1" | jq -r '.decision // .data.decision')

echo "Decision_LOW=$DEC1" | tee -a "$EVID/03_submit_urllc_low.json"

echo "--------------------------------------------------"
echo "FASE 3 — Teste URLLC (latência maior que RTT)"
echo "Esperado: PASS"
echo "--------------------------------------------------"

RESP2=$(curl -s -X POST "$PORTAL_URL" \
  -H "Content-Type: application/json" \
  -d "{
        \"slice_type\": \"URLLC\",
        \"sla_requirements\": {
          \"latency\": { \"max_ms\": $HIGH_LAT }
        }
      }")

echo "$RESP2" | tee "$EVID/04_submit_urllc_high.json"

DEC2=$(echo "$RESP2" | jq -r '.decision // .data.decision')

echo "Decision_HIGH=$DEC2" | tee -a "$EVID/04_submit_urllc_high.json"

echo "--------------------------------------------------"
echo "FASE 4 — Validação Determinística"
echo "--------------------------------------------------"

if [[ "$DEC1" == "FAIL" && "$DEC2" == "ACCEPT" ]]; then
  echo "RESULTADO: PASS (Determinístico)" | tee "$EVID/05_validation.txt"
else
  echo "RESULTADO: FAIL (Comportamento inesperado)" | tee "$EVID/05_validation.txt"
fi

echo "--------------------------------------------------"
echo "FASE 5 — Atualização Runbook"
echo "--------------------------------------------------"

HASH_BEFORE=$(sha256sum "$RUNBOOK" | awk '{print $1}')

cat <<EOF >> "$RUNBOOK"

### PROMPT_SNASP_32 — E2E Deterministic Validation

**Data:** $(date -u +"%Y-%m-%dT%H:%M:%SZ")

Teste E2E via Portal:

- URLLC com latency < RTT real → $DEC1
- URLLC com latency > RTT real → $DEC2

Validação determinística do domínio Transporte + Headroom.

Status: $(if [[ "$DEC1" == "FAIL" && "$DEC2" == "ACCEPT" ]]; then echo "PASS"; else echo "FAIL"; fi)

Evidências: evidencias_nasp/32_e2e_deterministic/

EOF

HASH_AFTER=$(sha256sum "$RUNBOOK" | awk '{print $1}')

echo "Hash Before: $HASH_BEFORE" | tee -a "$EVID/00_metadata.txt"
echo "Hash After : $HASH_AFTER" | tee -a "$EVID/00_metadata.txt"

echo "=================================================="
echo "PROMPT_SNASP_32 FINALIZADO"
echo "=================================================="
