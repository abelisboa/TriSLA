#!/usr/bin/env bash
set -euo pipefail

# ==========================================================
# TriSLA — GHCR Cleanup + Public Enforcement
# Autor: Abel Lisboa
# Objetivo:
#   - Deletar versões antigas dos containers GHCR
#   - Manter apenas versões recentes
#   - Tornar todos os packages públicos
#   - Gerar relatório de auditoria
# ==========================================================

OWNER="${OWNER:-abelisboa}"
KEEP_VERSIONS="${KEEP_VERSIONS:-1}"   # Quantas versões manter por package
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REPORT_DIR="./ghcr_cleanup_report_$STAMP"

mkdir -p "$REPORT_DIR"

log() { echo "[$(date -u +%H:%M:%S)] $*"; }
fail() { echo "ERROR: $*" >&2; exit 1; }

need() { command -v "$1" >/dev/null 2>&1 || fail "comando ausente: $1"; }

need gh
need jq

log "=========================================================="
log "GHCR CLEANUP — OWNER: $OWNER"
log "Mantendo apenas $KEEP_VERSIONS versão(ões) mais recente(s)"
log "Relatório: $REPORT_DIR"
log "=========================================================="

log "[1/5] Listando packages tipo container..."

PACKAGES=$(gh api \
  -H "Accept: application/vnd.github+json" \
  "/users/$OWNER/packages?package_type=container" \
  --paginate | jq -r '.[].name')

if [ -z "$PACKAGES" ]; then
  log "Nenhum package container encontrado."
  exit 0
fi

echo "$PACKAGES" > "$REPORT_DIR/packages.txt"

for PKG in $PACKAGES; do
  log "------------------------------------------"
  log "Processando package: $PKG"

  # Tornar público
  log "→ Garantindo visibilidade pública"
  gh api \
    -X PATCH \
    -H "Accept: application/vnd.github+json" \
    "/users/$OWNER/packages/container/$PKG/visibility" \
    -f visibility=public >/dev/null || true

  # Listar versões
  log "→ Listando versões"
  VERSIONS_JSON=$(gh api \
    -H "Accept: application/vnd.github+json" \
    "/users/$OWNER/packages/container/$PKG/versions" \
    --paginate)

  echo "$VERSIONS_JSON" > "$REPORT_DIR/${PKG}_versions.json"

  VERSION_IDS=$(echo "$VERSIONS_JSON" \
    | jq -r 'sort_by(.created_at) | reverse | .[].id')

  COUNT=0
  for VID in $VERSION_IDS; do
    COUNT=$((COUNT+1))

    if [ "$COUNT" -le "$KEEP_VERSIONS" ]; then
      log "✓ Mantendo versão ID: $VID"
      continue
    fi

    log "✗ Deletando versão ID: $VID"
    gh api \
      -X DELETE \
      -H "Accept: application/vnd.github+json" \
      "/users/$OWNER/packages/container/$PKG/versions/$VID" \
      || log "Falha ao deletar versão $VID (talvez já deletada)"
  done

done

log "=========================================================="
log "CLEANUP FINALIZADO"
log "Relatório salvo em: $REPORT_DIR"
log "=========================================================="
