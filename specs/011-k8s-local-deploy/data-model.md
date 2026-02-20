# Data Model: Kubernetes Resources

**Feature**: 011-k8s-local-deploy
**Date**: 2026-02-20
**Status**: Complete

## Overview

This document defines the Kubernetes resource models for deploying Lumina Todo services. Unlike traditional data models (database entities), this feature deals with Kubernetes resource definitions.

## Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: lumina
  labels:
    app.kubernetes.io/name: lumina-todo
    app.kubernetes.io/managed-by: helm
```

## Resource Models by Service

### Frontend Service

#### Deployment

| Field | Value | Notes |
|-------|-------|-------|
| name | frontend | |
| replicas | 1 | Scalable |
| image | lumina-frontend:latest | Local build |
| containerPort | 3000 | Next.js default |
| resources.requests.cpu | 250m | |
| resources.requests.memory | 256Mi | |
| resources.limits.cpu | 500m | |
| resources.limits.memory | 512Mi | |

**Environment Variables**:
| Name | Source | Description |
|------|--------|-------------|
| NEXT_PUBLIC_API_URL | ConfigMap | Backend API URL |
| NODE_ENV | ConfigMap | production |

**Probes**:
| Probe | Path | Port | Initial Delay | Period |
|-------|------|------|---------------|--------|
| liveness | / | 3000 | 15s | 30s |
| readiness | / | 3000 | 5s | 10s |

#### Service

| Field | Value | Notes |
|-------|-------|-------|
| name | frontend-service | |
| type | NodePort | External access |
| port | 3000 | Service port |
| targetPort | 3000 | Container port |
| nodePort | 30080 | External access |

#### ConfigMap

| Key | Value |
|-----|-------|
| NEXT_PUBLIC_API_URL | http://backend-service.lumina.svc.cluster.local:8000 |
| NODE_ENV | production |

---

### Backend Service

#### Deployment

| Field | Value | Notes |
|-------|-------|-------|
| name | backend | |
| replicas | 1 | **Fixed** (SQLite) |
| image | lumina-backend:latest | Local build |
| containerPort | 8000 | FastAPI default |
| resources.requests.cpu | 250m | |
| resources.requests.memory | 256Mi | |
| resources.limits.cpu | 500m | |
| resources.limits.memory | 512Mi | |

**Environment Variables (ConfigMap)**:
| Name | Source | Description |
|------|--------|-------------|
| DATABASE_URL | ConfigMap | SQLite path |
| CHATBOT_URL | ConfigMap | Chatbot service URL |
| ENVIRONMENT | ConfigMap | production |
| CORS_ORIGINS | ConfigMap | Allowed origins |

**Environment Variables (Secret)**:
| Name | Source | Description |
|------|--------|-------------|
| JWT_SECRET_KEY | Secret | Auth signing key |
| SMTP_USER | Secret | Email credentials |
| SMTP_PASS | Secret | Email credentials |

**Volume Mounts**:
| Name | Mount Path | Purpose |
|------|------------|---------|
| sqlite-data | /app/data | SQLite database |

**Probes**:
| Probe | Path | Port | Initial Delay | Period |
|-------|------|------|---------------|--------|
| liveness | /api/health | 8000 | 15s | 30s |
| readiness | /api/health | 8000 | 5s | 10s |

#### Service

| Field | Value | Notes |
|-------|-------|-------|
| name | backend-service | |
| type | ClusterIP | Internal only |
| port | 8000 | Service port |
| targetPort | 8000 | Container port |

#### ConfigMap

| Key | Value |
|-----|-------|
| DATABASE_URL | sqlite:///app/data/lumina.db |
| CHATBOT_URL | http://chatbot-service.lumina.svc.cluster.local:8001 |
| ENVIRONMENT | production |
| CORS_ORIGINS | http://frontend-service.lumina.svc.cluster.local:3000 |

#### Secret

| Key | Description | Template |
|-----|-------------|----------|
| JWT_SECRET_KEY | JWT signing key | .Values.backend.secrets.jwtSecretKey |
| SMTP_USER | Gmail address | .Values.backend.secrets.smtpUser |
| SMTP_PASS | Gmail app password | .Values.backend.secrets.smtpPass |

#### PersistentVolumeClaim

| Field | Value | Notes |
|-------|-------|-------|
| name | backend-sqlite-pvc | |
| accessModes | ReadWriteOnce | Single pod access |
| storage | 1Gi | SQLite database |
| storageClassName | standard | Minikube default |

---

### Chatbot Service

#### Deployment

| Field | Value | Notes |
|-------|-------|-------|
| name | chatbot | |
| replicas | 1 | Scalable |
| image | lumina-chatbot:latest | Local build |
| containerPort | 8001 | MCP server |
| resources.requests.cpu | 250m | |
| resources.requests.memory | 256Mi | |
| resources.limits.cpu | 500m | |
| resources.limits.memory | 512Mi | |

**Environment Variables (ConfigMap)**:
| Name | Source | Description |
|------|--------|-------------|
| MCP_SERVER_PORT | ConfigMap | 8001 |
| MCP_SERVER_HOST | ConfigMap | 0.0.0.0 |
| ENVIRONMENT | ConfigMap | production |
| BACKEND_URL | ConfigMap | Backend API URL |

**Environment Variables (Secret)**:
| Name | Source | Description |
|------|--------|-------------|
| OPENROUTER_API_KEY | Secret | LLM API key |

**Probes**:
| Probe | Path | Port | Initial Delay | Period |
|-------|------|------|---------------|--------|
| liveness | /health | 8001 | 15s | 30s |
| readiness | /health | 8001 | 5s | 10s |

#### Service

| Field | Value | Notes |
|-------|-------|-------|
| name | chatbot-service | |
| type | ClusterIP | Internal only |
| port | 8001 | Service port |
| targetPort | 8001 | Container port |

#### ConfigMap

| Key | Value |
|-----|-------|
| MCP_SERVER_PORT | 8001 |
| MCP_SERVER_HOST | 0.0.0.0 |
| ENVIRONMENT | production |
| BACKEND_URL | http://backend-service.lumina.svc.cluster.local:8000 |

#### Secret

| Key | Description | Template |
|-----|-------------|----------|
| OPENROUTER_API_KEY | OpenRouter/OpenAI API key | .Values.chatbot.secrets.openrouterApiKey |

---

## Labels and Selectors

All resources use consistent labels for Kubernetes best practices:

```yaml
labels:
  app.kubernetes.io/name: {{ .Chart.Name }}
  app.kubernetes.io/instance: {{ .Release.Name }}
  app.kubernetes.io/version: {{ .Chart.AppVersion }}
  app.kubernetes.io/component: {{ frontend | backend | chatbot }}
  app.kubernetes.io/part-of: lumina-todo
  app.kubernetes.io/managed-by: helm
```

**Selector Labels** (used in Deployments and Services):
```yaml
selector:
  matchLabels:
    app.kubernetes.io/name: {{ .Chart.Name }}
    app.kubernetes.io/instance: {{ .Release.Name }}
```

## Resource Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                    Namespace: lumina                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │   Frontend   │   │   Backend    │   │   Chatbot    │    │
│  │  Deployment  │   │  Deployment  │   │  Deployment  │    │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘    │
│         │                  │                   │            │
│         │                  │                   │            │
│  ┌──────▼───────┐   ┌──────▼───────┐   ┌──────▼───────┐    │
│  │   Service    │   │   Service    │   │   Service    │    │
│  │  (NodePort)  │   │  (ClusterIP) │   │  (ClusterIP) │    │
│  │    30080     │   │    8000      │   │    8001      │    │
│  └──────────────┘   └──────┬───────┘   └──────────────┘    │
│                            │                                │
│                     ┌──────▼───────┐                        │
│                     │     PVC      │                        │
│                     │  sqlite-data │                        │
│                     └──────────────┘                        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    ConfigMaps                         │  │
│  │  frontend-config | backend-config | chatbot-config   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                     Secrets                           │  │
│  │            backend-secrets | chatbot-secrets          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Service Communication Flow

```
External User
     │
     ▼ (NodePort 30080)
┌─────────────┐
│  Frontend   │
│    :3000    │
└──────┬──────┘
       │ HTTP (K8s DNS)
       ▼
┌─────────────┐
│  Backend    │◄──────────────┐
│    :8000    │               │
└──────┬──────┘               │
       │ HTTP (K8s DNS)       │
       ▼                      │
┌─────────────┐               │
│  Chatbot    │───────────────┘
│    :8001    │  (tools callback)
└─────────────┘
```

## Validation Rules

### Deployment Constraints
- Backend replicas MUST be 1 (SQLite single-writer)
- All containers MUST run as non-root
- All containers MUST have resource limits

### Service Constraints
- Only frontend uses NodePort
- Backend and Chatbot use ClusterIP
- All services must be in `lumina` namespace

### Secret Constraints
- Secrets MUST NOT be committed to git
- Values provided via `--set` or separate values file
- Template files use placeholders only
