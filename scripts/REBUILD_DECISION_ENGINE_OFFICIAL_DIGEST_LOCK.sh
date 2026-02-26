#!/usr/bin/env bash
set -euo pipefail

NS="${NS:-trisla}"
RELEASE="${RELEASE:-trisla}"
CHART_DIR="${CHART_DIR:-./helm/trisla}"
VALUES_FILE="${VALUES_FILE:-$CHART_DIR/values.yaml}"

APP_DIR="${APP_DIR:-./apps/decision-engine}"
IMAGE_REPO="${IMAGE_REPO:-ghcr.io/abelisboa/trisla-decision-engine}"
IMAGE_TAG="${IMAGE_TAG:-v3.11.2}"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="./evidencias_decision_engine_rebuild/${STAMP}"

log(){ echo "[$(date -u +%H:%M:%S)] $*"; }
fail(){ echo "ERROR: $*" >&2; exit 1; }

need(){ command -v "$1" >/dev/null 2>&1 || fail "comando ausente: $1"; }

need helm
need kubectl
need python3

# Podman/Docker compat
if command -v podman >/dev/null 2>&1; then
  OCI="podman"
elif command -v docker >/dev/null 2>&1; then
  OCI="docker"
else
  fail "nem podman nem docker encontrados"
fi

mkdir -p "$OUT_DIR"

log "=========================================================="
log "REBUILD OFICIAL DECISION ENGINE + DIGEST LOCK"
log "Namespace:  $NS"
log "Release:    $RELEASE"
log "Chart:      $CHART_DIR"
log "Values:     $VALUES_FILE"
log "App Dir:    $APP_DIR"
log "Image Repo: $IMAGE_REPO"
log "Image Tag:  $IMAGE_TAG"
log "Evidências: $OUT_DIR"
log "=========================================================="

[ -d "$APP_DIR" ] || fail "APP_DIR não encontrado: $APP_DIR"
[ -f "$VALUES_FILE" ] || fail "values.yaml não encontrado: $VALUES_FILE"

log "[1/8] Backup values.yaml"
cp -a "$VALUES_FILE" "$OUT_DIR/values.yaml.before"

log "[2/8] Build da imagem (local)"
$OCI build -t "${IMAGE_REPO}:${IMAGE_TAG}" "$APP_DIR" | tee "$OUT_DIR/build.log"

log "[3/8] Push para GHCR"
$OCI push "${IMAGE_REPO}:${IMAGE_TAG}" | tee "$OUT_DIR/push.log"

log "[4/8] Obtendo digest oficial (RepoDigest)"
# Para podman: podman inspect --format '{{index .RepoDigests 0}}'
REPO_DIGEST="$($OCI inspect --format '{{index .RepoDigests 0}}' "${IMAGE_REPO}:${IMAGE_TAG}" 2>/dev/null || true)"
if [ -z "${REPO_DIGEST:-}" ]; then
  fail "RepoDigest vazio após push. Verifique push.log."
fi
# extrai só sha256:...
DIGEST="$(echo "$REPO_DIGEST" | awk -F'@' '{print $2}')"
[ -n "$DIGEST" ] || fail "não foi possível extrair digest do RepoDigest: $REPO_DIGEST"

log "Digest oficial: $DIGEST"
echo "$REPO_DIGEST" > "$OUT_DIR/repo_digest.txt"
echo "$DIGEST" > "$OUT_DIR/digest.txt"

log "[5/8] Patch values.yaml: decisionEngine.image.tag=\"\" e decisionEngine.image.digest=\"$DIGEST\""
python3 - <<PY
import yaml
from pathlib import Path

p = Path("$VALUES_FILE")
data = yaml.safe_load(p.read_text())

data.setdefault("decisionEngine", {})
data["decisionEngine"].setdefault("image", {})

img = data["decisionEngine"]["image"]
img["repository"] = "trisla-decision-engine"
img["tag"] = ""              # DIGEST LOCK
img["digest"] = "$DIGEST"
# pullPolicy não precisa ser Always em digest; manter IfNotPresent é ok
img.setdefault("pullPolicy", "IfNotPresent")

p.write_text(yaml.safe_dump(data, sort_keys=False))
print("OK: decisionEngine.image atualizado para digest-lock")
PY

cp -a "$VALUES_FILE" "$OUT_DIR/values.yaml.after"

log "[6/8] helm lint"
helm lint "$CHART_DIR" | tee "$OUT_DIR/helm_lint.txt"

log "[7/8] helm template (validar imagem renderizada)"
helm template "$RELEASE" "$CHART_DIR" -n "$NS" > "$OUT_DIR/render.yaml"

grep -n "trisla-decision-engine" "$OUT_DIR/render.yaml" | tee "$OUT_DIR/render_decision_engine_lines.txt" || true
if ! grep -q "ghcr.io/abelisboa/trisla-decision-engine@${DIGEST}" "$OUT_DIR/render.yaml"; then
  fail "render não contém a imagem esperada: ghcr.io/abelisboa/trisla-decision-engine@${DIGEST}"
fi

log "[8/8] Aplicando helm upgrade e reiniciando apenas decision-engine"
helm upgrade --install "$RELEASE" "$CHART_DIR" -n "$NS" | tee "$OUT_DIR/helm_upgrade.txt"

# Remove pods em ImagePullBackOff do decision-engine (só dele)
kubectl -n "$NS" get pods | awk '/^trisla-decision-engine-/{ if ($3=="ImagePullBackOff") print $1 }' \
  | xargs -r kubectl -n "$NS" delete pod

kubectl -n "$NS" rollout status deploy/trisla-decision-engine --timeout=240s | tee "$OUT_DIR/rollout.txt" || true

log "=========================================================="
log "REBUILD DECISION ENGINE CONCLUÍDO"
log "Evidências: $OUT_DIR"
log "=========================================================="
