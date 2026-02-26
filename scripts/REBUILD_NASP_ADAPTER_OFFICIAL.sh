#!/usr/bin/env bash
set -euo pipefail

IMAGE="ghcr.io/abelisboa/trisla-nasp-adapter:v3.11.2"
VALUES_FILE="./helm/trisla/values.yaml"

log() { echo "[$(date -u +%H:%M:%S)] $*"; }
fail() { echo "ERROR: $*" >&2; exit 1; }

need() { command -v "$1" >/dev/null 2>&1 || fail "comando ausente: $1"; }

need docker
need helm
need awk
need sed

log "=========================================================="
log "REBUILD OFICIAL DO NASP ADAPTER"
log "=========================================================="

log "[1/6] Build da imagem"
docker build -t $IMAGE apps/trisla-nasp-adapter

log "[2/6] Push para GHCR"
docker push $IMAGE

log "[3/6] Obtendo digest"
DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' $IMAGE | awk -F@ '{print $2}')

[ -n "$DIGEST" ] || fail "Digest não encontrado"

log "Digest oficial: $DIGEST"

log "[4/6] Atualizando values.yaml"

awk -v digest="$DIGEST" '
/repository: trisla-nasp-adapter/ {print; getline; print "    tag: \"\""; print "    digest: \""digest"\""; next}
{print}
' $VALUES_FILE > tmp.yaml

mv tmp.yaml $VALUES_FILE

log "[5/6] Testando helm"
helm lint helm/trisla
helm template trisla helm/trisla -n trisla > /dev/null

log "[6/6] Validando render"
helm template trisla helm/trisla -n trisla | grep trisla-nasp-adapter

log "=========================================================="
log "NASP ADAPTER AGORA É OFICIAL + DIGEST-LOCKED"
log "=========================================================="
