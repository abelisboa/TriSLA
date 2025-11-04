{{/*
Expand the name of the chart.
*/}}
{{- define "trisla.name" -}}
trisla
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "trisla.fullname" -}}
{{- printf "%s" (include "trisla.name" .) -}}
{{- end }}

{{/*
Common labels
*/}}
{{- define "trisla.labels" -}}
app.kubernetes.io/name: {{ include "trisla.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
{{- end }}
