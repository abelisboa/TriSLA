#!/usr/bin/env bash
set -euo pipefail

NS="${NS:-trisla}"
RELEASE="${RELEASE:-trisla}"
CHART_DIR="${CHART_DIR:-./helm/trisla}"
VALUES_FILE="${VALUES_FILE:-$CHART_DIR/values.yaml}"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="./evidencias_kafka_public_fix/${STAMP}"

log(){ echo "[$(date -u +%H:%M:%S)] $*"; }
fail(){ echo "ERROR: $*" >&2; exit 1; }

mkdir -p "$OUT_DIR"

log "=========================================================="
log "FIX KAFKA → MODO PUBLIC TAG (SEM SECRET, SEM DIGEST)"
log "=========================================================="

cp -a "$VALUES_FILE" "$OUT_DIR/values.before.yaml"

python3 - <<PY
import yaml
from pathlib import Path

p = Path("$VALUES_FILE")
data = yaml.safe_load(p.read_text())

data.setdefault("kafka", {})
data["kafka"].setdefault("image", {})

img = data["kafka"]["image"]
img["repository"] = "ghcr.io/abelisboa/trisla-kafka"
img["tag"] = "v3.11.2"
img["digest"] = ""
img["pullPolicy"] = "IfNotPresent"

# Remover imagePullSecrets globais se existirem
data["imagePullSecrets"] = []

p.write_text(yaml.safe_dump(data, sort_keys=False))
print("OK: Kafka configurado como imagem pública por TAG.")
PY

cp -a "$VALUES_FILE" "$OUT_DIR/values.after.yaml"

log "[1/3] helm upgrade"
helm upgrade --install "$RELEASE" "$CHART_DIR" -n "$NS"

log "[2/3] deletando pods Kafka antigos"
kubectl -n "$NS" delete pod -l app=kafka --ignore-not-found

log "[3/3] aguardando rollout"
kubectl -n "$NS" rollout status deploy/kafka --timeout=180s || true

log "=========================================================="
log "KAFKA AJUSTADO PARA MODO PUBLIC"
log "=========================================================="
