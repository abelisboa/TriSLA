#!/usr/bin/env bash
set -euo pipefail

NS="${NS:-trisla}"
RELEASE="${RELEASE:-trisla}"
CHART_DIR="${CHART_DIR:-./helm/trisla}"
VALUES_FILE="${VALUES_FILE:-$CHART_DIR/values.yaml}"

APP_DIR="${APP_DIR:-./apps/trisla-kafka}"
IMAGE_REPO="ghcr.io/abelisboa/trisla-kafka"
IMAGE_TAG="v3.11.2"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="./evidencias_kafka_rebuild/${STAMP}"

log(){ echo "[$(date -u +%H:%M:%S)] $*"; }
fail(){ echo "ERROR: $*" >&2; exit 1; }

need(){ command -v "$1" >/dev/null 2>&1 || fail "comando ausente: $1"; }

need helm
need kubectl
need python3

if command -v podman >/dev/null 2>&1; then
  OCI="podman"
elif command -v docker >/dev/null 2>&1; then
  OCI="docker"
else
  fail "nem podman nem docker encontrados"
fi

mkdir -p "$OUT_DIR"

log "=========================================================="
log "REBUILD OFICIAL KAFKA + DIGEST LOCK"
log "Namespace:  $NS"
log "App Dir:    $APP_DIR"
log "Image Repo: $IMAGE_REPO"
log "Image Tag:  $IMAGE_TAG"
log "=========================================================="

[ -d "$APP_DIR" ] || fail "APP_DIR não encontrado: $APP_DIR"
[ -f "$VALUES_FILE" ] || fail "values.yaml não encontrado"

cp -a "$VALUES_FILE" "$OUT_DIR/values.before.yaml"

log "[1/6] Build da imagem Kafka"
$OCI build -t "${IMAGE_REPO}:${IMAGE_TAG}" "$APP_DIR" | tee "$OUT_DIR/build.log"

log "[2/6] Push para GHCR"
$OCI push "${IMAGE_REPO}:${IMAGE_TAG}" | tee "$OUT_DIR/push.log"

log "[3/6] Obtendo RepoDigest"
REPO_DIGEST="$($OCI inspect --format '{{index .RepoDigests 0}}' "${IMAGE_REPO}:${IMAGE_TAG}")"
DIGEST="$(echo "$REPO_DIGEST" | awk -F'@' '{print $2}')"

[ -n "$DIGEST" ] || fail "Digest não encontrado"

echo "$DIGEST" > "$OUT_DIR/digest.txt"
log "Digest oficial Kafka: $DIGEST"

log "[4/6] Patch values.yaml para digest-lock"
python3 - <<PY
import yaml
from pathlib import Path

p = Path("$VALUES_FILE")
data = yaml.safe_load(p.read_text())

data.setdefault("kafka", {})
data["kafka"].setdefault("image", {})

img = data["kafka"]["image"]
img["repository"] = "ghcr.io/abelisboa/trisla-kafka"
img["tag"] = ""
img["digest"] = "$DIGEST"
img["pullPolicy"] = "IfNotPresent"

p.write_text(yaml.safe_dump(data, sort_keys=False))
print("OK: kafka.image atualizado")
PY

cp -a "$VALUES_FILE" "$OUT_DIR/values.after.yaml"

log "[5/6] helm upgrade"
helm upgrade --install "$RELEASE" "$CHART_DIR" -n "$NS" | tee "$OUT_DIR/helm_upgrade.log"

log "[6/6] Removendo pods Kafka antigos"
kubectl -n "$NS" delete pod -l app=kafka --ignore-not-found

kubectl -n "$NS" rollout status deploy/kafka --timeout=240s || true

log "=========================================================="
log "REBUILD KAFKA CONCLUÍDO"
log "=========================================================="
