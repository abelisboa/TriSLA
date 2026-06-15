{{/*
Portal image reference — digest-pinned SSOT (Wave 2 W2-B).
Usage: {{ include "portal.image" (dict "Values" .Values "image" .Values.backend.image) }}
*/}}
{{- define "portal.image" -}}
{{- $img := .image -}}
{{- $repo := default "" $img.repository -}}
{{- if eq $repo "" -}}
{{- fail "portal image repository not defined" -}}
{{- end -}}
{{- $digest := default "" $img.digest -}}
{{- if eq $digest "" -}}
{{- fail (printf "DIGEST REQUIRED for portal image %s. Tag-only refs are not SSOT." $repo) -}}
{{- end -}}
{{ printf "%s@%s" $repo $digest }}
{{- end -}}
