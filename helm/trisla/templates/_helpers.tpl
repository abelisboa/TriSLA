{{/* Chart name */}}
{{- define "trisla.name" -}}
trisla
{{- end }}

{{/* Labels */}}
{{- define "trisla.labels" -}}
app.kubernetes.io/name: {{ include "trisla.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: {{ .component | default "trisla" }}
app.kubernetes.io/version: {{ .Values.global.version | default .Chart.AppVersion | default "3.6.0" }}
{{- end }}

{{/* Selector labels */}}
{{- define "trisla.selectorLabels" -}}
app.kubernetes.io/name: {{ include "trisla.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/* Image builder */}}
{{- define "trisla.image" -}}
{{- $image := .image -}}
{{- $registry := .Values.global.imageRegistry | default .Values.global.registry | default "ghcr.io/abelisboa" -}}
{{- printf "%s/%s:%s" $registry $image.repository $image.tag -}}
{{- end }}
