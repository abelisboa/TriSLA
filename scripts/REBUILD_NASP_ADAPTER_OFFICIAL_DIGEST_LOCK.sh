#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="ghcr.io/abelisboa/trisla-nasp-adapter"
IMAGE_TAG="v3.11.2"
BUILD_DIR="./apps/nasp-adapter"
VALUES_FILE="./helm/trisla/values.yaml"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
EVID_DIR="./evidencias_nasp_rebuild/${STAMP}"

log() { echo "[$(date -u +%H:%M:%S)] $*"; }
fail() { echo "ERROR: $*" >&2; exit 1; }

need() { command -v "$1" >/dev/null 2>&1 || fail "comando ausente: $1"; }

need docker
need helm
need awk
need sed
need mkdir
need grep

log "=========================================================="
log "REBUILD OFICIAL NASP ADAPTER + DIGEST LOCK"
log "Build Dir: $BUILD_DIR"
log "=========================================================="

[ -d "$BUILD_DIR" ] || fail "Diretório não encontrado: $BUILD_DIR"

mkdir -p "$EVID_DIR"

# ----------------------------------------------------------
# 1) Build
# ----------------------------------------------------------
log "[1/7] Build da imagem"
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} "$BUILD_DIR" | tee "$EVID_DIR/build.log"

# ----------------------------------------------------------
# 2) Push
# ----------------------------------------------------------
log "[2/7] Push para GHCR"
docker push ${IMAGE_NAME}:${IMAGE_TAG} | tee "$EVID_DIR/push.log"

# ----------------------------------------------------------
# 3) Obter digest oficial
# ----------------------------------------------------------
log "[3/7] Obtendo digest"
DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' ${IMAGE_NAME}:${IMAGE_TAG} | awk -F@ '{print $2}')
[ -n "$DIGEST" ] || fail "Digest não encontrado"

echo "$DIGEST" > "$EVID_DIR/digest.txt"
log "Digest oficial: $DIGEST"

# ----------------------------------------------------------
# 4) Atualizar values.yaml para modo digest
# ----------------------------------------------------------
log "[4/7] Atualizando values.yaml"

awk -v digest="$DIGEST" '
/repository: trisla-nasp-adapter/ {
    print;
    getline;
    print "    tag: \"\"";
    print "    digest: \""digest"\"";
    next
}
{print}
' "$VALUES_FILE" > "$EVID_DIR/values.tmp"

mv "$EVID_DIR/values.tmp" "$VALUES_FILE"

# ----------------------------------------------------------
# 5) Helm lint
# ----------------------------------------------------------
log "[5/7] helm lint"
helm lint helm/trisla | tee "$EVID_DIR/helm_lint.log"

# ----------------------------------------------------------
# 6) Validar render
# ----------------------------------------------------------
log "[6/7] helm template"
helm template trisla helm/trisla -n trisla > "$EVID_DIR/render.yaml"

grep trisla-nasp-adapter "$EVID_DIR/render.yaml" | tee "$EVID_DIR/render_check.txt"

# ----------------------------------------------------------
# 7) Verificação final
# ----------------------------------------------------------
if grep -q "@sha256" "$EVID_DIR/render_check.txt"; then
    log "NASP Adapter está 100% em modo DIGEST LOCK"
else
    fail "NASP Adapter NÃO está usando digest"
fi

log "=========================================================="
log "REBUILD NASP ADAPTER CONCLUÍDO COM SUCESSO"
log "Evidências: $EVID_DIR"
log "=========================================================="
