#!/usr/bin/env bash
set -euo pipefail

OWNER="abelisboa"
TOKEN="${GITHUB_TOKEN:?GITHUB_TOKEN não definido}"
KEEP_PREFIX="trisla-"

STAMP=$(date -u +%Y%m%dT%H%M%SZ)
REPORT="./ghcr_full_reset_${STAMP}.log"

log() { echo "[$(date -u +%H:%M:%S)] $*" | tee -a "$REPORT"; }

log "=========================================================="
log "GHCR FULL RESET — OWNER: $OWNER"
log "Mantendo apenas packages iniciados por: $KEEP_PREFIX"
log "Relatório: $REPORT"
log "=========================================================="

# Listar todos packages container
PACKAGES=$(gh api \
  -H "Accept: application/vnd.github+json" \
  /users/$OWNER/packages?package_type=container \
  --jq '.[].name')

for pkg in $PACKAGES; do
  if [[ "$pkg" == ${KEEP_PREFIX}* ]]; then
    log "✓ Mantendo package: $pkg"
  else
    log "✗ Deletando package inteiro: $pkg"
    gh api \
      -X DELETE \
      -H "Accept: application/vnd.github+json" \
      /users/$OWNER/packages/container/$pkg \
      || log "Falha ao deletar $pkg (talvez já removido)"
  fi
done

log "----------------------------------------------------------"
log "Tornando todos packages $KEEP_PREFIX públicos"

for pkg in $(gh api \
  -H "Accept: application/vnd.github+json" \
  /users/$OWNER/packages?package_type=container \
  --jq '.[].name'); do

  if [[ "$pkg" == ${KEEP_PREFIX}* ]]; then
    log "→ Ajustando visibilidade para PUBLIC: $pkg"

    gh api \
      -X PATCH \
      -H "Accept: application/vnd.github+json" \
      /users/$OWNER/packages/container/$pkg/visibility \
      -f visibility=public \
      || log "Falha ao tornar público $pkg"
  fi
done

log "=========================================================="
log "RESET COMPLETO FINALIZADO"
log "Verifique: https://github.com/$OWNER?tab=packages"
log "=========================================================="
