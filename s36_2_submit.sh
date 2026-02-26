#!/usr/bin/env bash
set -euo pipefail
BASE="evidencias_release_v3.9.11/s36_2_kafka_fix/03_submit"
mkdir -p "$BASE"

submit() {
  local scenario="$1" stype="$2" fname="$3"
  local ts out
  ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  out="$BASE/${fname}.json"
  curl -sS -m 30 -o "$out" -X POST "http://127.0.0.1:18080/api/v1/sla/submit" \
    -H "Content-Type: application/json" \
    -d "{\"template_id\":\"template:${stype}\",\"form_values\":{\"service_type\":\"${stype}\",\"latency_ms\":10,\"throughput_mbps\":50,\"reliability\":0.999}}"
  echo "${fname} submitted at ${ts}" >&2
  sleep 4
}

submit "A" "URLLC" "submit_A"
submit "B" "eMBB"  "submit_B"
submit "C" "mMTC"  "submit_C"
echo "[OK] Submissions done. Outputs in $BASE"
