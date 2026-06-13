#!/usr/bin/env bash
# RC-P20-09 — Controlled digest deployment (portal backend + frontend only).
set -euo pipefail

REPO="${REPO_ROOT:-/home/porvir5g/gtp5g/trisla}"
cd "$REPO"

BUILD_TS="$(date -u +%Y%m%dT%H%M%SZ)"
PACK="${REPO}/evidencias_trisla_rc_p20_09_${BUILD_TS}"
mkdir -p "$PACK"/{build,deploy,runtime,payloads,validation,screenshots,rollback,checksums}

echo "=== RC-P20-09 deploy pack=${PACK} ==="

# Record prior digests (rollback)
{
  echo "prior_backend=$(kubectl -n trisla get deploy trisla-portal-backend -o jsonpath='{.spec.template.spec.containers[0].image}')"
  echo "prior_frontend=$(kubectl -n trisla get deploy trisla-portal-frontend -o jsonpath='{.spec.template.spec.containers[0].image}')"
} | tee "$PACK/rollback/prior_images.env"

kubectl -n trisla get deploy trisla-portal-backend trisla-portal-frontend -o yaml \
  > "$PACK/runtime/deployments_before.yaml"

# Unit tests (pre-build gate)
podman run --rm -v "${REPO}/apps/portal-backend:/app:Z" -w /app docker.io/library/python:3.10-slim \
  bash -c "pip install -q -r requirements.txt pytest httpx pydantic-settings && PYTHONPATH=/app python -m pytest tests/test_explainability_recovery.py tests/test_admission_compliance_wiring.py tests/test_sla_status_schema_alignment.py -q" \
  2>&1 | tee "$PACK/build/backend_tests.txt"

cd apps/portal-frontend
npm ci >/dev/null 2>&1 || npm install
npx tsx src/lib/complianceSeparation.test.ts 2>&1 | tee "$PACK/build/complianceSeparation.test.txt"
npx tsx src/lib/explainabilityRecovery.test.ts 2>&1 | tee "$PACK/build/explainabilityRecovery.test.txt"
npm run build 2>&1 | tee "$PACK/build/frontend_build.txt"
cd "$REPO"

git rev-parse HEAD | tee "$PACK/build/commit.txt"

# GHCR build + push (digest captured via skopeo)
podman build --format docker -t "ghcr.io/abelisboa/trisla-portal-backend:${BUILD_TS}" \
  -f apps/portal-backend/Dockerfile apps/portal-backend \
  2>&1 | tee "$PACK/build/backend_build.log"
podman push "ghcr.io/abelisboa/trisla-portal-backend:${BUILD_TS}" 2>&1 | tee "$PACK/build/backend_push.log"
BACKEND_DIGEST=$(skopeo inspect "docker://ghcr.io/abelisboa/trisla-portal-backend:${BUILD_TS}" | jq -r .Digest)

podman build --format docker -t "ghcr.io/abelisboa/trisla-portal-frontend:${BUILD_TS}" \
  -f apps/portal-frontend/Dockerfile apps/portal-frontend \
  2>&1 | tee "$PACK/build/frontend_build.log"
podman push "ghcr.io/abelisboa/trisla-portal-frontend:${BUILD_TS}" 2>&1 | tee "$PACK/build/frontend_push.log"
FRONTEND_DIGEST=$(skopeo inspect "docker://ghcr.io/abelisboa/trisla-portal-frontend:${BUILD_TS}" | jq -r .Digest)

{
  echo "build_ts=${BUILD_TS}"
  echo "backend_digest=${BACKEND_DIGEST}"
  echo "frontend_digest=${FRONTEND_DIGEST}"
  echo "backend_image=ghcr.io/abelisboa/trisla-portal-backend@${BACKEND_DIGEST}"
  echo "frontend_image=ghcr.io/abelisboa/trisla-portal-frontend@${FRONTEND_DIGEST}"
} | tee "$PACK/build/digests.env"

# Pin helm values
python3 - <<PY
from pathlib import Path
import re
p = Path("$REPO/helm/trisla-portal/values.yaml")
text = p.read_text()
text = re.sub(
    r'(backend:\n(?:.*\n)*?    digest: )"sha256:[a-f0-9]+"',
    rf'\1"${BACKEND_DIGEST}"',
    text,
    count=1,
)
text = re.sub(
    r'(frontend:\n(?:.*\n)*?    digest: )"sha256:[a-f0-9]+"',
    rf'\1"${FRONTEND_DIGEST}"',
    text,
    count=1,
)
p.write_text(text)
PY

helm upgrade trisla-portal "$REPO/helm/trisla-portal" -n trisla \
  2>&1 | tee "$PACK/deploy/helm_upgrade.log"
kubectl -n trisla rollout status deployment/trisla-portal-backend --timeout=300s \
  2>&1 | tee "$PACK/deploy/backend_rollout.log"
kubectl -n trisla rollout status deployment/trisla-portal-frontend --timeout=300s \
  2>&1 | tee "$PACK/deploy/frontend_rollout.log"

kubectl -n trisla get deploy trisla-portal-backend trisla-portal-frontend -o yaml \
  > "$PACK/runtime/deployments_after.yaml"

# Verify deployment / pod / helm alignment
BE_DEPLOY=$(kubectl -n trisla get deploy trisla-portal-backend -o jsonpath='{.spec.template.spec.containers[0].image}')
FE_DEPLOY=$(kubectl -n trisla get deploy trisla-portal-frontend -o jsonpath='{.spec.template.spec.containers[0].image}')
BE_POD=$(kubectl -n trisla get pods -l app=trisla-portal-backend -o jsonpath='{.items[0].status.containerStatuses[0].imageID}')
FE_POD=$(kubectl -n trisla get pods -l app=trisla-portal-frontend -o jsonpath='{.items[0].status.containerStatuses[0].imageID}')
HELM_BE=$(grep -A2 'backend:' "$REPO/helm/trisla-portal/values.yaml" | grep digest | sed 's/.*"\(sha256:[^"]*\)".*/\1/')
HELM_FE=$(grep -A2 'frontend:' "$REPO/helm/trisla-portal/values.yaml" | grep digest | sed 's/.*"\(sha256:[^"]*\)".*/\1/')

{
  echo "backend_deployment=${BE_DEPLOY}"
  echo "backend_pod=${BE_POD}"
  echo "backend_helm=${HELM_BE}"
  echo "frontend_deployment=${FE_DEPLOY}"
  echo "frontend_pod=${FE_POD}"
  echo "frontend_helm=${HELM_FE}"
} | tee "$PACK/deploy/image_alignment.txt"

# Non-regression: other components unchanged
kubectl -n trisla get deployment trisla-decision-engine trisla-sem-csmf trisla-sla-agent-layer trisla-bc-nssmf \
  -o jsonpath='{range .items[*]}{.metadata.name}{"="}{.spec.template.spec.containers[0].image}{"\n"}{end}' \
  | tee "$PACK/validation/non_regression_images.txt"

echo "PACK=${PACK}" | tee "$PACK/build/pack_path.txt"
echo "DONE backend=${BACKEND_DIGEST} frontend=${FRONTEND_DIGEST}"
