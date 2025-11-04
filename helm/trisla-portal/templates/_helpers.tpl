{{/*
Expand the name of the chart.
*/}}
{{- define "trisla-portal.name" -}}
trisla-portal
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "trisla-portal.fullname" -}}
{{- printf "%s" (include "trisla-portal.name" .) -}}
{{- end }}

{{/*
Common labels
*/}}
{{- define "trisla-portal.labels" -}}
app.kubernetes.io/name: {{ include "trisla-portal.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
{{- end }}
