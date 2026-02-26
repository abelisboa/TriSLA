#!/usr/bin/env bash
set -euo pipefail

VALUES_FILE="${VALUES_FILE:-./helm/trisla/values.yaml}"

log() { echo "[$(date -u +%H:%M:%S)] $*"; }
fail() { echo "ERROR: $*" >&2; exit 1; }

need() { command -v "$1" >/dev/null 2>&1 || fail "comando ausente: $1"; }

need docker
need awk
need sed

[ -f "$VALUES_FILE" ] || fail "values.yaml não encontrado"

log "=========================================================="
log "Fix NASP Adapter para modo DIGEST"
log "=========================================================="

IMAGE="ghcr.io/abelisboa/trisla-nasp-adapter:v3.9.22"

log "[1/4] Pull da imagem"
docker pull $IMAGE >/dev/null

DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' $IMAGE | awk -F@ '{print $2}')

if [ -z "$DIGEST" ]; then
  fail "Não foi possível obter digest"
fi

log "Digest encontrado: $DIGEST"

log "[2/4] Atualizando values.yaml"

# Remove tag
sed -i '/repository: trisla-nasp-adapter/{n; s/tag:.*/tag: ""/}' $VALUES_FILE

# Adiciona digest abaixo do tag
awk -v digest="$DIGEST" '
/repository: trisla-nasp-adapter/ {print; getline; print; print "    digest: \""digest"\""; next}
{print}
' $VALUES_FILE > tmp.yaml

mv tmp.yaml $VALUES_FILE

log "[3/4] Testando render"
helm template trisla helm/trisla -n trisla > /dev/null || fail "helm template falhou"

log "[4/4] Validando saída"
helm template trisla helm/trisla -n trisla | grep trisla-nasp-adapter

log "=========================================================="
log "NASP ADAPTER AGORA ESTÁ DIGEST-LOCKED"
log "=========================================================="
