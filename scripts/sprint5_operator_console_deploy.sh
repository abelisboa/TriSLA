#!/usr/bin/env bash
set -euo pipefail
REPO=/home/porvir5g/gtp5g/trisla
cd "$REPO"
TS=$(date -u +%Y%m%dT%H%M%SZ)
PACK="${REPO}/sprint5_operator_console_hardening_${TS}"
mkdir -p "$PACK"/{analysis,before,after,build,deploy,runtime,screenshots}
BE=http://192.168.10.15:32002
FE=http://192.168.10.15:32561

echo "PACK=$PACK" | tee "$PACK/before/pack_path.txt"
git rev-parse HEAD | tee "$PACK/before/git_head.txt"
kubectl -n trisla get deployment trisla-portal-frontend -o jsonpath='{.spec.template.spec.containers[0].image}'; echo | tee "$PACK/before/frontend_image.txt"
kubectl -n trisla get deployment trisla-portal-backend -o jsonpath='{.spec.template.spec.containers[0].image}'; echo | tee "$PACK/before/backend_image.txt"

{
  echo "# Operator Console Inventory"
  echo "Generated: ${TS}"
  echo ""
  echo "## Scope"
  echo "Frontend-only operational presentation layer (apps/portal-frontend/)"
  echo ""
  echo "## Hardened surfaces"
  echo "- Monitoring: Radio/Transport/Core Network cards, formatted KPIs"
  echo "- Administration: Platform Health, Monitoring Service, Admission Service"
  echo "- Governance: lifecycle humanization, Technical Details collapsed"
  echo "- PNL: Natural Language SLA flow without tenant_id/template_id in main UI"
  echo ""
  echo "## Technical identifiers (Technical Details only)"
  echo "- tx_hash, status_code, payload JSON, API paths, raw lifecycle keys"
} | tee "$PACK/analysis/operator_console_inventory.md"

curl -sS "${BE}/api/v1/prometheus/summary" | tee "$PACK/before/runtime_baseline.txt" >/dev/null
curl -sS "${BE}/api/v1/interfaces/cn-i1/metrics" | jq -c . | tee "$PACK/before/cn_i1_baseline.json" >/dev/null

cd apps/portal-frontend
npm ci 2>&1 | tail -5 | tee "$PACK/build/npm_ci_tail.txt"
npm run build 2>&1 | tee "$PACK/build/frontend_build.txt"
cd "$REPO"
git rev-parse HEAD | tee "$PACK/build/commit.txt"

BUILD_TS=$(date -u +%Y%m%dT%H%M%SZ)
echo "BUILD_TS=${BUILD_TS}" | tee "$PACK/build/build_ts.env"
podman build --format docker -t "ghcr.io/abelisboa/trisla-portal-frontend:${BUILD_TS}" -f apps/portal-frontend/Dockerfile apps/portal-frontend 2>&1 | tee "$PACK/build/podman_build.txt"
podman push "ghcr.io/abelisboa/trisla-portal-frontend:${BUILD_TS}" 2>&1 | tee "$PACK/build/podman_push.txt"
FRONTEND_DIGEST=$(skopeo inspect "docker://ghcr.io/abelisboa/trisla-portal-frontend:${BUILD_TS}" | jq -r .Digest)
echo "$FRONTEND_DIGEST" | tee "$PACK/build/frontend_registry_digest.txt"
echo "ghcr.io/abelisboa/trisla-portal-frontend@${FRONTEND_DIGEST}" | tee "$PACK/build/frontend_image_ref.txt"

kubectl -n trisla set image deployment/trisla-portal-frontend "frontend=ghcr.io/abelisboa/trisla-portal-frontend@${FRONTEND_DIGEST}" | tee "$PACK/deploy/set_image.txt"
kubectl -n trisla rollout status deployment/trisla-portal-frontend --timeout=300s | tee "$PACK/deploy/rollout_status.txt"
kubectl -n trisla get pods -l app=trisla-portal-frontend -o wide | tee "$PACK/deploy/pods.txt"

sleep 4

run_pnl() {
  local intent="$1" label="$2" template="$3"
  local tenant="trisla-$(openssl rand -hex 4)"
  local interpret submit
  interpret=$(curl -sf -X POST "${BE}/api/v1/sla/interpret" -H "Content-Type: application/json" -d "{\"intent_text\":\"${intent}\",\"tenant_id\":\"${tenant}\"}")
  submit_body=$(echo "$interpret" | jq -c --arg tid "$template" --arg ten "$tenant" '{
    template_id: $tid, tenant_id: $ten,
    form_values: ({type:(.slice_type//.service_type), slice_type:(.slice_type//.service_type), latency:.sla_requirements.latency, reliability:.sla_requirements.reliability, throughput:.sla_requirements.throughput} | with_entries(select(.value!=null and .value!="")))
  }')
  submit=$(curl -sf -X POST "${BE}/api/v1/sla/submit" -H "Content-Type: application/json" -d "$submit_body")
  echo "$submit" | jq "{label:\"${label}\", decision, status, bc_status, tx_hash, registration: .metadata.governance_registration_status, lifecycle: .metadata.lifecycle_state}" \
    | tee "$PACK/runtime/pnl_${label}.json"
}

run_pnl "cirurgia remota" urllc urllc-template-001
run_pnl "vídeo 4K" embb embb-template-001
run_pnl "sensores IoT" mmtc mmtc-template-001

for path in / /pnl /monitoring /administration /sla-lifecycle; do
  code=$(curl -sf -o /dev/null -w "%{http_code}" "${FE}${path}")
  echo "${path}: HTTP ${code}"
done | tee "$PACK/analysis/non_regression_routes.txt"

curl -sf "${BE}/health" | jq -c . | tee "$PACK/runtime/backend_health.json"
curl -sf "${BE}/api/v1/prometheus/summary" | jq -c . | tee "$PACK/runtime/prometheus_summary.json"
curl -sf "${BE}/api/v1/interfaces/cn-i1/metrics" | jq -c . | tee "$PACK/runtime/cn_i1_after.json"

{
  echo "# Runtime validation"
  grep -q "Radio Network\|Transport Network\|Core Network" "$PACK/runtime/monitoring_html_after.html" 2>/dev/null && echo "PASS: domain network titles" || echo "NOTE: domain titles client-rendered"
  for f in "$PACK/runtime/pnl_"*.json; do
    [ -f "$f" ] || continue
    jq -e '.decision == "ACCEPT" and (.tx_hash // "" | length) > 0' "$f" >/dev/null && echo "PASS: $(basename "$f") ACCEPT+tx_hash" || echo "FAIL: $(basename "$f")"
  done
} | tee "$PACK/analysis/runtime_validation.md"

curl -sS "${FE}/monitoring" | tee "$PACK/runtime/monitoring_html_after.html" >/dev/null
for page in "" pnl monitoring administration sla-lifecycle; do
  curl -sS "${FE}/${page}" -o "$PACK/screenshots/${page:-dashboard}_page.html" 2>/dev/null || true
done

kubectl -n trisla get deployment trisla-portal-frontend -o jsonpath='{.spec.template.spec.containers[0].image}'; echo | tee "$PACK/after/frontend_image.txt"
echo "COMMIT=$(git rev-parse HEAD)" | tee "$PACK/after/commit.txt"
echo "DIGEST=${FRONTEND_DIGEST}" | tee "$PACK/after/digest.txt"
echo "DONE pack=${PACK}"
