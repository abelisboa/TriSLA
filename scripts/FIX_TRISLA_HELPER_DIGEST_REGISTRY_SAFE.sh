#!/usr/bin/env bash
set -euo pipefail

# ==========================================================
# TriSLA — HELPER FIX (Digest + Registry Safe)
# Corrige definitivamente o helper trisla.image
# Compatível com:
#   - dict parcial (sem .Values)
#   - dict completo (com .Values)
# Garante prefixo do registry + suporte a digest
# ==========================================================

NS="${NS:-trisla}"
RELEASE="${RELEASE:-trisla}"
CHART_DIR="${CHART_DIR:-./helm/trisla}"
HELPERS="${CHART_DIR}/templates/_helpers.tpl"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_DIR="./evidencias_helper_fix/${STAMP}"

log() { echo "[$(date -u +%H:%M:%S)] $*"; }
fail() { echo "ERROR: $*" >&2; exit 1; }

need() { command -v "$1" >/dev/null 2>&1 || fail "comando ausente: $1"; }

need helm
need awk
need sed
need diff
need cp
need mkdir

log "=========================================================="
log "TriSLA HELPER FIX — Digest + Registry Safe"
log "Chart: $CHART_DIR"
log "Helpers: $HELPERS"
log "Backup: $BACKUP_DIR"
log "=========================================================="

[ -f "$HELPERS" ] || fail "_helpers.tpl não encontrado"

mkdir -p "$BACKUP_DIR"

# ----------------------------------------------------------
# 1) Backup
# ----------------------------------------------------------
log "[1/6] Backup do helper"
cp -a "$HELPERS" "$BACKUP_DIR/_helpers.tpl.before"

# ----------------------------------------------------------
# 2) Nova função definitiva
# ----------------------------------------------------------
log "[2/6] Gerando função definitiva"

cat > "$BACKUP_DIR/trisla.image.new.tpl" <<'EOF'
{{- define "trisla.image" -}}
{{- /*
TriSLA image resolver — versão definitiva
Compatível com chamadas:
  include "trisla.image" (dict "image" .Values.xxx.image)
  include "trisla.image" (dict "image" .Values.xxx.image "Values" .Values)

Prioridade:
  1) image.full
  2) repository + digest
  3) repository + tag
*/ -}}

{{- $img := .image -}}
{{- $vals := .Values | default $.Values -}}

{{- if $img.full -}}
  {{- $img.full -}}
{{- else -}}

  {{- $repo := $img.repository -}}

  {{- $firstPart := (splitList "/" $repo | first) -}}
  {{- $hasRegistry := contains "." $firstPart -}}

  {{- if not $hasRegistry -}}
    {{- $repo = printf "%s/%s" ($vals.global.imageRegistry | default "ghcr.io/abelisboa") $repo -}}
  {{- end -}}

  {{- if $img.digest -}}
    {{- printf "%s@%s" $repo $img.digest -}}
  {{- else -}}
    {{- printf "%s:%s" $repo ($img.tag | default "latest") -}}
  {{- end -}}

{{- end -}}
{{- end -}}
EOF

# ----------------------------------------------------------
# 3) Aplicar patch (idempotente)
# ----------------------------------------------------------
log "[3/6] Aplicando patch no helper"

TMP_FILE="$(mktemp)"
cp "$HELPERS" "$TMP_FILE"

if grep -q 'define "trisla.image"' "$TMP_FILE"; then
  awk '
    BEGIN {inblock=0}
    /define "trisla.image"/ {inblock=1; system("cat '"$BACKUP_DIR/trisla.image.new.tpl"'"); next}
    inblock==1 && /end/ {inblock=0; next}
    inblock==0 {print}
  ' "$TMP_FILE" > "${TMP_FILE}.patched"
else
  cat "$TMP_FILE" > "${TMP_FILE}.patched"
  echo "" >> "${TMP_FILE}.patched"
  cat "$BACKUP_DIR/trisla.image.new.tpl" >> "${TMP_FILE}.patched"
fi

if diff -q "$HELPERS" "${TMP_FILE}.patched" >/dev/null 2>&1; then
  log "Nenhuma alteração necessária (já atualizado)."
else
  cp "${TMP_FILE}.patched" "$HELPERS"
  log "Helper atualizado com sucesso."
fi

rm -f "$TMP_FILE" "${TMP_FILE}.patched"

cp -a "$HELPERS" "$BACKUP_DIR/_helpers.tpl.after"

# ----------------------------------------------------------
# 4) Helm lint
# ----------------------------------------------------------
log "[4/6] Executando helm lint"
helm lint "$CHART_DIR" > "$BACKUP_DIR/helm_lint.txt" || fail "helm lint falhou"

# ----------------------------------------------------------
# 5) Teste de render
# ----------------------------------------------------------
log "[5/6] Testando helm template"
helm template "$RELEASE" "$CHART_DIR" -n "$NS" > "$BACKUP_DIR/helm_template.yaml" || fail "helm template falhou"

grep 'image:' "$BACKUP_DIR/helm_template.yaml" > "$BACKUP_DIR/rendered_images.txt"

# ----------------------------------------------------------
# 6) Validação final
# ----------------------------------------------------------
log "[6/6] Validando se registry está sendo aplicado"

if grep -q 'image: trisla-' "$BACKUP_DIR/rendered_images.txt"; then
  fail "Registry NÃO está sendo aplicado corretamente"
fi

log "=========================================================="
log "FIX CONCLUÍDO COM SUCESSO"
log "Evidências: $BACKUP_DIR"
log "=========================================================="
