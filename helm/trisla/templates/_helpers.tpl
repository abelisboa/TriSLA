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
{{/* IMAGE HELPER — DIGEST ONLY (ABSOLUTO)                     */}}
{{/* ========================================================== */}}

{{- define "trisla.image" -}}

{{- $img := .image -}}
{{- $vals := .Values -}}

{{- if and $img.full (ne $img.full "") -}}
{{- $img.full -}}
{{- else -}}

{{- $repo := default "" $img.repository -}}

{{- if eq $repo "" -}}
{{- fail "repository da imagem não definido" -}}
{{- end -}}

{{- $firstPart := (splitList "/" $repo | first) -}}
{{- $hasRegistry := or (contains "." $firstPart) (contains ":" $firstPart) -}}

{{- if not $hasRegistry -}}
{{- $registry := default "ghcr.io/abelisboa" $vals.global.imageRegistry -}}
{{- $repo = printf "%s/%s" $registry $repo -}}
{{- end -}}

{{- $digest := default "" $img.digest -}}

{{- if eq $digest "" -}}
{{- fail (printf "DIGEST OBRIGATÓRIO para %s. TAG NÃO É PERMITIDA." $repo) -}}
{{- end -}}

{{ printf "%s@%s" $repo $digest }}

{{- end -}}
{{- end -}}
