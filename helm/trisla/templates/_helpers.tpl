{{/*
Common labels
*/}}
{{- define "trisla.labels" -}}
app.kubernetes.io/name: {{ include "trisla.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/component: {{ .component | default "trisla" }}
app.kubernetes.io/part-of: trisla
{{- end }}

{{/*
Selector labels
*/}}
{{- define "trisla.selectorLabels" -}}
app.kubernetes.io/name: {{ include "trisla.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: {{ .component | default "trisla" }}
{{- end }}

{{/*
Chart name
*/}}
{{- define "trisla.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Full image name
*/}}
{{- define "trisla.image" -}}
{{- if .Values.global.imageRegistry }}
{{- printf "%s/%s:%s" .Values.global.imageRegistry .repository .tag }}
{{- else }}
{{- printf "%s:%s" .repository .tag }}
{{- end }}
{{- end }}

{{/*
GHCR Docker Config JSON (Base64 encoded)
Only used when ghcrUser and ghcrToken are provided
*/}}
{{- define "trisla.ghcrDockerConfig" -}}
{{- $auth := printf "%s:%s" .Values.global.ghcrUser .Values.global.ghcrToken | b64enc }}
{{- $config := printf "{\"auths\":{\"%s\":{\"username\":\"%s\",\"password\":\"%s\",\"auth\":\"%s\"}}}" .Values.global.imageRegistry .Values.global.ghcrUser .Values.global.ghcrToken $auth }}
{{- $config | b64enc }}
{{- end }}

