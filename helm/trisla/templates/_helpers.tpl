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
{{/* IMAGE HELPER — Digest + Registry Safe (DEFINITIVO)        */}}
{{/* ========================================================== */}}

{{- define "trisla.image" -}}

{{- $img := .image -}}
{{- $vals := .Values -}}

{{- /* Se imagem full já vier pronta, usa direto */ -}}
{{- if and $img.full (ne $img.full "") -}}
{{- $img.full -}}
{{- else -}}

{{- /* ------------------------- */ -}}
{{- /* Resolver repository       */ -}}
{{- /* ------------------------- */ -}}

{{- $repo := default "" $img.repository -}}

{{- if eq $repo "" -}}
{{- fail "repository da imagem não definido" -}}
{{- end -}}

{{- /* Verifica se já possui registry explícito */ -}}
{{- $firstPart := (splitList "/" $repo | first) -}}
{{- $hasRegistry := or (contains "." $firstPart) (contains ":" $firstPart) -}}

{{- if not $hasRegistry -}}
{{- $registry := default "ghcr.io/abelisboa" $vals.global.imageRegistry -}}
{{- $repo = printf "%s/%s" $registry $repo -}}
{{- end -}}

{{- /* ------------------------- */ -}}
{{- /* Resolver digest ou tag    */ -}}
{{- /* ------------------------- */ -}}

{{- $digest := default "" $img.digest -}}
{{- $tag := default "" $img.tag -}}

{{- if ne $digest "" -}}
{{ printf "%s@%s" $repo $digest }}
{{- else -}}
{{- if eq $tag "" -}}
{{ printf "%s:latest" $repo }}
{{- else -}}
{{ printf "%s:%s" $repo $tag }}
{{- end -}}
{{- end -}}

{{- end -}}
{{- end -}}
