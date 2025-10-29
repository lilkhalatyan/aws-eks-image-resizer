{{- define "image-resizer.labels" -}}
app.kubernetes.io/name: image-resizer
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}