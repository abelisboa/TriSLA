#!/usr/bin/env bash
set -euo pipefail
REPO=/home/porvir5g/gtp5g/trisla
cd "$REPO"
TS=$(date -u +%Y%m%dT%H%M%SZ)
PACK="${REPO}/sprint5c_observability_promql_alignment_${TS}"
mkdir -p "$PACK"/{before,analysis,evidence,build,deploy,runtime,after}
BE=http://192.168.10.15:32002
FE=http://192.168.10.15:32561

git fetch origin main && git pull origin main
git rev-parse HEAD | tee "$PACK/before/git_head.txt"
{
  echo -n "frontend="
  kubectl -n trisla get deployment trisla-portal-frontend -o jsonpath='{.spec.template.spec.containers[0].image}'; echo
  echo -n "backend_before="
  kubectl -n trisla get deployment trisla-portal-backend -o jsonpath='{.spec.template.spec.containers[0].image}'; echo
} | tee "$PACK/before/runtime_baseline.txt"

curl -sS "${BE}/api/v1/prometheus/summary" | tee "$PACK/before/summary_before.json" >/dev/null
curl -sS "${BE}/api/v1/interfaces/tn-i1/metrics" | tee "$PACK/before/tn_i1_before.json" >/dev/null
curl -sS "${BE}/api/v1/interfaces/cn-i1/metrics" | tee "$PACK/before/cn_i1_before.json" >/dev/null

cat > "$PACK/analysis/promql_inventory.md" << 'MD'
# PromQL Inventory — Sprint 5C

| Surface | Key | Source |
|---------|-----|--------|
| Summary CPU | `cluster_cpu_percent` | `CLUSTER_CPU_PERCENT_SUMMARY` |
| Summary latency | `transport_latency_ms` | `PROMQL_SSOT["TRANSPORT_RTT"]` |
| TN-I1 latency | `TN_I1_LATENCY_DEFAULT` | probe RTT SSOT |
| TN-I1 jitter | `TN_I1_JITTER_DEFAULT` | probe jitter SSOT |
| CN-I1 | unchanged Sprint 5A | container metrics ns-1274485 |
MD

cat > "$PACK/analysis/cpu_alignment_plan.md" << 'MD'
# CPU Alignment Plan

**Before:** `node_cpu_seconds_total` denominator → 0 series → `cpu: null`  
**After:** container CPU share `trisla` / all containers × 100 (Sprint 5B validated)
MD

cat > "$PACK/analysis/jitter_alignment_plan.md" << 'MD'
# Jitter Alignment Plan

**Before:** `avg(trisla_transport_jitter_ms)` → 0 series  
**After:** `PROMQL_SSOT["TRANSPORT_JITTER"]` probe max-min over 1m × 1000
MD

podman run --rm -v "${REPO}/apps/portal-backend:/app:Z" -w /app docker.io/library/python:3.10-slim \
  bash -c "pip install -q -r requirements.txt pytest && PYTHONPATH=/app python -m pytest tests/test_observability_promql_ssot.py tests/test_cn_i1_promql_ssot.py tests/test_prometheus_response.py -q" \
  2>&1 | tee "$PACK/analysis/unit_tests.md"

BUILD_TS=$(date -u +%Y%m%dT%H%M%SZ)
echo "BUILD_TS=${BUILD_TS}" | tee "$PACK/build/build_ts.env"
podman build --format docker -t "ghcr.io/abelisboa/trisla-portal-backend:${BUILD_TS}" \
  -f apps/portal-backend/Dockerfile apps/portal-backend \
  2>&1 | tee "$PACK/build/backend_build.txt"
podman push "ghcr.io/abelisboa/trisla-portal-backend:${BUILD_TS}" 2>&1 | tee "$PACK/build/backend_push.txt"
BACKEND_DIGEST=$(skopeo inspect "docker://ghcr.io/abelisboa/trisla-portal-backend:${BUILD_TS}" | jq -r .Digest)
echo "$BACKEND_DIGEST" | tee "$PACK/build/backend_registry_digest.txt"
git rev-parse HEAD | tee "$PACK/build/commit.txt"

kubectl -n trisla set image deployment/trisla-portal-backend \
  backend="ghcr.io/abelisboa/trisla-portal-backend@${BACKEND_DIGEST}" \
  2>&1 | tee "$PACK/deploy/set_image.txt"
kubectl -n trisla rollout status deployment/trisla-portal-backend --timeout=300s 2>&1 | tee "$PACK/deploy/rollout_status.txt"
kubectl -n trisla get pods -l app=trisla-portal-backend -o wide 2>&1 | tee "$PACK/deploy/pods.txt"

sleep 5
curl -sS "${BE}/api/v1/prometheus/summary" | tee "$PACK/runtime/summary_after.json" | jq .
curl -sS "${BE}/api/v1/interfaces/tn-i1/metrics" | tee "$PACK/runtime/tn_i1_after.json" | jq .
curl -sS "${BE}/api/v1/interfaces/cn-i1/metrics" | tee "$PACK/runtime/cn_i1_after.json" | jq .

{
  echo "# Functional validation"
  jq -e '.cpu != null' "$PACK/runtime/summary_after.json" && echo "PASS: CPU summary non-null" || echo "FAIL: CPU summary null"
  jq -e '.metrics.jitter_ms != null' "$PACK/runtime/tn_i1_after.json" && echo "PASS: TN-I1 jitter non-null" || echo "FAIL: TN-I1 jitter null"
  jq -e '.metrics.latency_ms != null' "$PACK/runtime/tn_i1_after.json" && echo "PASS: TN-I1 latency non-null" || echo "FAIL: TN-I1 latency null"
  jq -e '.metrics.cpu_utilization != null and .metrics.memory_utilization != null' "$PACK/runtime/cn_i1_after.json" && echo "PASS: CN-I1 unchanged" || echo "FAIL: CN-I1"
} | tee "$PACK/analysis/runtime_validation.md"

tenant="trisla-$(openssl rand -hex 4)"
interpret=$(curl -sf -X POST "${BE}/api/v1/sla/interpret" -H "Content-Type: application/json" -d "{\"intent_text\":\"cirurgia remota\",\"tenant_id\":\"${tenant}\"}")
submit_body=$(echo "$interpret" | jq -c --arg ten "$tenant" '{
  template_id: "urllc-template-001", tenant_id: $ten,
  form_values: ({type:(.slice_type//.service_type), slice_type:(.slice_type//.service_type), latency:.sla_requirements.latency, reliability:.sla_requirements.reliability} | with_entries(select(.value!=null and .value!="")))
}')
curl -sf -X POST "${BE}/api/v1/sla/submit" -H "Content-Type: application/json" -d "$submit_body" \
  | jq '{decision, bc_status, tx_hash}' | tee "$PACK/runtime/pnl_regression.json"

for path in /monitoring /administration /pnl; do
  code=$(curl -sf -o /dev/null -w "%{http_code}" "${FE}${path}")
  echo "${path}: HTTP ${code}"
done | tee "$PACK/analysis/non_regression_routes.txt"

kubectl -n trisla get deployment trisla-portal-backend -o jsonpath='{.spec.template.spec.containers[0].image}'; echo | tee "$PACK/after/backend_image.txt"
echo "DIGEST=${BACKEND_DIGEST}" | tee "$PACK/after/digest.txt"
echo "DONE pack=${PACK}"
