#!/usr/bin/env bash
set -euo pipefail

CHART_DIR="${CHART_DIR:-./helm/trisla}"
HELPERS="${CHART_DIR}/templates/_helpers.tpl"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_DIR="./evidencias_helper_reset/${STAMP}"

log() { echo "[$(date -u +%H:%M:%S)] $*"; }
fail() { echo "ERROR: $*" >&2; exit 1; }

need() { command -v "$1" >/dev/null 2>&1 || fail "comando ausente: $1"; }

need helm
need awk
need sed
need cp
need mkdir

[ -f "$HELPERS" ] || fail "_helpers.tpl não encontrado"

mkdir -p "$BACKUP_DIR"

log "=========================================================="
log "RESET COMPLETO DO HELPER trisla.image"
log "Backup: $BACKUP_DIR"
log "=========================================================="

# Backup
cp -a "$HELPERS" "$BACKUP_DIR/_helpers.tpl.before"

# Remover qualquer definição antiga da função
awk '
BEGIN {skip=0}
/define "trisla.image"/ {skip=1; next}
skip==1 && /end/ {skip=0; next}
skip==0 {print}
' "$HELPERS" > "${HELPERS}.clean"

# Substituir helpers pelo arquivo limpo
mv "${HELPERS}.clean" "$HELPERS"

# Adicionar nova função no final
cat >> "$HELPERS" <<'EOF'

{{- define "trisla.image" -}}
{{- /*
TriSLA image resolver — versão final estável
Requer include com:
include "trisla.image" (dict "image" .Values.xxx.image "Values" .Values)
*/ -}}

{{- $img := .image -}}
{{- $vals := .Values -}}

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

cp -a "$HELPERS" "$BACKUP_DIR/_helpers.tpl.after"

log "[1/2] helm lint"
helm lint "$CHART_DIR" > "$BACKUP_DIR/helm_lint.txt" || fail "helm lint falhou"

log "[2/2] helm template"
helm template trisla "$CHART_DIR" -n trisla > "$BACKUP_DIR/render.yaml" || fail "helm template falhou"

log "=========================================================="
log "RESET CONCLUÍDO COM SUCESSO"
log "=========================================================="
