#!/usr/bin/env bash
set -euo pipefail

CHART_DIR="${CHART_DIR:-./helm/trisla}"
HELPERS="${CHART_DIR}/templates/_helpers.tpl"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_DIR="./evidencias_helpers_rebuild/${STAMP}"

log() { echo "[$(date -u +%H:%M:%S)] $*"; }
fail() { echo "ERROR: $*" >&2; exit 1; }

need() { command -v "$1" >/dev/null 2>&1 || fail "comando ausente: $1"; }

need helm
need cp
need mkdir

[ -f "$HELPERS" ] || fail "_helpers.tpl não encontrado"

mkdir -p "$BACKUP_DIR"

log "=========================================================="
log "REBUILD COMPLETO DO _helpers.tpl"
log "Backup: $BACKUP_DIR"
log "=========================================================="

cp -a "$HELPERS" "$BACKUP_DIR/_helpers.tpl.before"

cat > "$HELPERS" <<'EOF'
{{/* ========================================================== */}}
{{/* TriSLA — CLEAN HELPERS                                    */}}
{{/* ========================================================== */}}

{{- define "trisla.name" -}}
{{- .Chart.Name -}}
{{- end -}}

{{- define "trisla.selectorLabels" -}}
app.kubernetes.io/name: {{ include "trisla.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "trisla.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{ include "trisla.selectorLabels" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/* ========================================================== */}}
{{/* IMAGE HELPER — Digest + Registry Safe                      */}}
{{/* ========================================================== */}}

{{- define "trisla.image" -}}
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
log "HELPERS RECONSTRUÍDO COM SUCESSO"
log "=========================================================="
