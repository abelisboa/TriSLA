#!/usr/bin/env bash
set -euo pipefail

NS="${NS:-trisla}"
RELEASE="${RELEASE:-trisla}"
CHART_DIR="${CHART_DIR:-./helm/trisla}"
VALUES_FILE="${VALUES_FILE:-$CHART_DIR/values.yaml}"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="./evidencias_kafka_pin/${STAMP}"

log(){ echo "[$(date -u +%H:%M:%S)] $*"; }
fail(){ echo "ERROR: $*" >&2; exit 1; }

need(){ command -v "$1" >/dev/null 2>&1 || fail "comando ausente: $1"; }

need kubectl
need helm
need python3

mkdir -p "$OUT_DIR"

log "=========================================================="
log "PIN KAFKA — travar digest do pod Running + corrigir rollout"
log "Namespace:  $NS"
log "Release:    $RELEASE"
log "Chart:      $CHART_DIR"
log "Values:     $VALUES_FILE"
log "Evidências: $OUT_DIR"
log "=========================================================="

[ -f "$VALUES_FILE" ] || fail "values.yaml não encontrado: $VALUES_FILE"

log "[1/7] Descobrindo pod Kafka RUNNING"
KAFKA_RUNNING="$(kubectl -n "$NS" get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.phase}{"\t"}{range .status.containerStatuses[*]}{.ready}{"\n"}{end}{end}' \
  | awk '$1 ~ /^kafka-/ && $2=="Running" {print $1; exit}')"

[ -n "${KAFKA_RUNNING:-}" ] || fail "não encontrei pod kafka-* em Running"

log "Pod Kafka Running: $KAFKA_RUNNING"

log "[2/7] Coletando image e imageID do Kafka Running"
kubectl -n "$NS" get pod "$KAFKA_RUNNING" -o json > "$OUT_DIR/kafka_running_pod.json"

IMAGE="$(python3 - <<PY
import json
d=json.load(open("$OUT_DIR/kafka_running_pod.json"))
cs=d["status"]["containerStatuses"][0]
print(cs.get("image",""))
PY
)"
IMAGEID="$(python3 - <<PY
import json
d=json.load(open("$OUT_DIR/kafka_running_pod.json"))
cs=d["status"]["containerStatuses"][0]
print(cs.get("imageID",""))
PY
)"

echo "$IMAGE"   > "$OUT_DIR/kafka_running_image.txt"
echo "$IMAGEID" > "$OUT_DIR/kafka_running_imageid.txt"

log "Kafka image:   $IMAGE"
log "Kafka imageID: $IMAGEID"

log "[3/7] Extraindo digest do imageID"
# imageID costuma vir como:
# docker-pullable://ghcr.io/abelisboa/trisla-kafka@sha256:...
# ou:
# ghcr.io/abelisboa/trisla-kafka@sha256:...
DIGEST="$(echo "$IMAGEID" | sed -E 's#^docker-pullable://##' | awk -F'@' '{print $2}')"
[ -n "${DIGEST:-}" ] || fail "não consegui extrair digest do imageID: $IMAGEID"

log "Digest detectado (Running): $DIGEST"
echo "$DIGEST" > "$OUT_DIR/digest.txt"

log "[4/7] Backup values.yaml"
cp -a "$VALUES_FILE" "$OUT_DIR/values.yaml.before"

log "[5/7] Patch values.yaml: kafka.image.tag=\"\" e kafka.image.digest=\"$DIGEST\""
python3 - <<PY
import yaml
from pathlib import Path

p = Path("$VALUES_FILE")
data = yaml.safe_load(p.read_text())

data.setdefault("kafka", {})
data["kafka"].setdefault("image", {})
img = data["kafka"]["image"]

# manter repo atual, mas garantir digest-lock
img["repository"] = "ghcr.io/abelisboa/trisla-kafka"
img["tag"] = ""
img["digest"] = "$DIGEST"
img.setdefault("pullPolicy", "IfNotPresent")

p.write_text(yaml.safe_dump(data, sort_keys=False))
print("OK: kafka.image atualizado para digest-lock do pod Running")
PY

cp -a "$VALUES_FILE" "$OUT_DIR/values.yaml.after"

log "[6/7] helm lint + upgrade"
helm lint "$CHART_DIR" | tee "$OUT_DIR/helm_lint.txt"
helm upgrade --install "$RELEASE" "$CHART_DIR" -n "$NS" | tee "$OUT_DIR/helm_upgrade.txt"

log "[7/7] Removendo apenas pods Kafka em ImagePullBackOff"
kubectl -n "$NS" get pods | awk '/^kafka-/{ if ($3=="ImagePullBackOff") print $1 }' \
  | xargs -r kubectl -n "$NS" delete pod

kubectl -n "$NS" rollout status deploy/kafka --timeout=240s | tee "$OUT_DIR/rollout.txt" || true

log "STATUS final:"
kubectl -n "$NS" get pods | tee "$OUT_DIR/pods_after.txt"

log "=========================================================="
log "PIN KAFKA CONCLUÍDO"
log "Evidências: $OUT_DIR"
log "=========================================================="
