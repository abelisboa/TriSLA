#!/usr/bin/env bash
set -euo pipefail
BASE="evidencias_release_v3.9.11/s36_1_control_latency"
REG="$BASE/01_registry/sla_registry.csv"
mkdir -p "$(dirname "$REG")"
echo "sla_id,intent_id,slice_type,scenario,submit_timestamp_utc" > "$REG"

submit() {
  local scenario="$1" stype="$2" fname="$3"
  local ts out
  ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  out="$BASE/01_registry/${fname}.json"
  curl -sS -m 30 -o "$out" -X POST "http://127.0.0.1:18080/api/v1/sla/submit" \
    -H "Content-Type: application/json" \
    -d "{\"template_id\":\"template:${stype}\",\"form_values\":{\"service_type\":\"${stype}\",\"latency_ms\":10,\"throughput_mbps\":50,\"reliability\":0.999}}"
  local sid iid
  sid=$(OUT_FILE="$out" python3 - <<'PY'
import json,os
try:
  j=json.load(open(os.environ.get("OUT_FILE","")))
  print(j.get("sla_id") or j.get("decision_id") or "")
except Exception: print("")
PY
)
  iid=$(OUT_FILE="$out" python3 - <<'PY'
import json,os
try:
  j=json.load(open(os.environ.get("OUT_FILE","")))
  print(j.get("intent_id") or "")
except Exception: print("")
PY
)
  echo "${sid},${iid},${stype},${scenario},${ts}" >> "$REG"
  sleep 3
}

submit "A" "URLLC" "submit_A"
submit "B" "eMBB"  "submit_B"
submit "C" "mMTC"  "submit_C"
submit "D" "URLLC" "submit_D"
echo "[OK] Submissions done. Registry: $REG"
