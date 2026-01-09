---
name: helm-guide
description: Fetch Helm documentation and apply chart best practices. Use when creating Helm charts, templates, or managing releases (Phase IV+).
version: 2.0.0
---

# Helm Chart Mastery Skill

## Context7 Research Results

**Library ID**: `/helm/helm`
**Source**: https://helm.sh/docs
**Reputation**: High

## When to Use This Skill

Activation triggers:
- Creating Helm charts for deployment
- Packaging K8s manifests as Helm charts
- Writing Helm templates with Go templating
- Managing releases with Helm

## Helm Chart Structure

```
todo-app/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration values
├── values.schema.json      # Values schema validation
├── templates/
│   ├── _helpers.tpl         # Named template helpers
│   ├── deployment.yaml      # Deployment template
│   ├── service.yaml         # Service template
│   ├── ingress.yaml         # Ingress template
│   ├── configmap.yaml       # ConfigMap template
│   ├── secrets.yaml         # Secret template
│   └── NOTES.txt            # Post-install instructions
└── tests/
    └── deployment_test.yaml # Chart tests
```

## Core Chart Files

### Chart.yaml

```yaml
apiVersion: v2
name: todo-app
description: Evolution of Todo - Full Stack Application
type: application
version: 1.0.0
appVersion: "1.0.0"
keywords:
  - todo
  - fastapi
  - nextjs
  - kubernetes
maintainers:
  - name: Evolution of Todo Team
    email: team@example.com
```

### values.yaml

```yaml
# Backend Configuration
backend:
  enabled: true
  replicaCount: 2
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 80
    targetPort: 8000
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  env:
    LOG_LEVEL: info

# Frontend Configuration
frontend:
  enabled: true
  replicaCount: 2
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 80
    targetPort: 3000
  resources:
    requests:
      memory: "128Mi"
      cpu: "50m"
    limits:
      memory: "256Mi"
      cpu: "200m"

# Ingress
ingress:
  enabled: true
  className: nginx
  annotations: {}
  hosts:
    - host: todo.local
      paths:
        - path: /api
          pathType: Prefix
          service: backend
        - path: /
          pathType: Prefix
          service: frontend

# Database (PostgreSQL)
postgres:
  enabled: true
  auth:
    database: todo
    username: todo
    password: changeme
  service:
    port: 5432
  persistence:
    enabled: true
    size: 1Gi

# Secrets reference
secrets:
  databaseUrl: ""
  authSecret: ""
```

### Template Example

```yaml
# templates/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}-backend
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
    component: backend
spec:
  replicas: {{ .Values.backend.replicaCount }}
  selector:
    matchLabels:
      {{- include "todo-app.selectorLabels" . | nindent 6 }}
      component: backend
  template:
    metadata:
      labels:
        {{- include "todo-app.selectorLabels" . | nindent 8 }}
        component: backend
    spec:
      containers:
      - name: backend
        image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
        imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
        ports:
        - name: http
          containerPort: {{ .Values.backend.service.targetPort }}
          protocol: TCP
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: {{ include "todo-app.fullname" . }}-secrets
              key: database-url
        - name: BETTER_AUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: {{ include "todo-app.fullname" . }}-secrets
              key: auth-secret
        resources:
          {{- toYaml .Values.backend.resources | nindent 10 }}
```

### Helper Templates (_helpers.tpl)

```yaml
# templates/_helpers.tpl
{{/*
Expand the name of the chart.
*/}}
{{- define "todo-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo-app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "todo-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-app.labels" -}}
helm.sh/chart: {{ include "todo-app.chart" . }}
{{ include "todo-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

## Helm Commands

```bash
# Lint chart
helm lint ./todo-app

# Template dry-run
helm template todo-app ./todo-app

# Install chart
helm install todo-app ./todo-app

# Install with values override
helm install todo-app ./todo-app -f custom-values.yaml

# Upgrade release
helm upgrade todo-app ./todo-app

# Rollback release
helm rollback todo-app 1

# Uninstall release
helm uninstall todo-app

# List releases
helm list

# Show values
helm show values ./todo-app
```

## Best Practices

| Practice | Implementation |
|----------|----------------|
| Named templates | Use `_helpers.tpl` for reusable templates |
| Values validation | Add `values.schema.json` |
| NOTES.txt | Post-install instructions for users |
| Labels | Include chart labels for discovery |
| Resource limits | Always configure in values.yaml |

## Context7 Query Patterns

| Topic | Query String |
|-------|--------------|
| Chart structure | "Helm chart structure Chart.yaml values.yaml" |
| Templating | "Helm template functions include define" |
| Dependencies | "Helm chart dependencies requirements.yaml" |
| Hooks | "Helm hooks pre-install post-install" |
