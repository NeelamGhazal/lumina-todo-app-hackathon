# Research: Local Kubernetes Deployment

**Feature**: 011-k8s-local-deploy
**Date**: 2026-02-20
**Status**: Complete

## Research Summary

All technical decisions have been resolved through spec clarification (Q1-Q3) and constitution alignment. No additional research was required as all patterns follow standard Kubernetes best practices.

## Technology Decisions

### 1. Container Build Strategy

**Decision**: Multi-stage Docker builds for all services

**Rationale**:
- Constitution mandates multi-stage builds (Phase IV standards)
- Reduces final image size by 60-80%
- Separates build dependencies from runtime
- Frontend: deps stage → build stage → nginx/node runtime
- Backend/Chatbot: build stage → slim Python runtime

**Alternatives Considered**:
- Single-stage builds: Larger images, security concerns (build tools in runtime)
- Buildpacks: Added complexity, less control

**Best Practices Applied**:
- Use `.dockerignore` to exclude node_modules, venv, __pycache__
- Pin base image versions (python:3.11-slim, node:20-alpine)
- Run as non-root user (appuser)
- Include HEALTHCHECK instructions

### 2. Helm Chart Architecture

**Decision**: Umbrella chart with subcharts

**Rationale**:
- Single `helm install` deploys entire stack
- Subcharts can be upgraded independently
- Shared values propagate to all services
- Clean separation of concerns

**Alternatives Considered**:
- Monolithic chart: Harder to maintain, no independent upgrades
- Separate charts: Requires 3 install commands, manual coordination

**Best Practices Applied**:
- Use `_helpers.tpl` for common labels and selectors
- Parameterize all configurable values
- Include resource requests/limits by default
- Add comprehensive values.yaml documentation

### 3. Service Discovery

**Decision**: Kubernetes DNS (resolved in spec Q1)

**Rationale**:
- Standard Kubernetes pattern
- Services accessible via `<name>.<namespace>.svc.cluster.local`
- Automatic DNS updates when pods restart
- No manual IP configuration

**Implementation**:
```yaml
# Frontend environment
NEXT_PUBLIC_API_URL: "http://backend-service.lumina.svc.cluster.local:8000"

# Backend environment
CHATBOT_URL: "http://chatbot-service.lumina.svc.cluster.local:8001"
```

### 4. Database Persistence

**Decision**: Single replica with PersistentVolumeClaim (resolved in spec Q2)

**Rationale**:
- SQLite requires single-writer access
- PVC ensures data survives pod restarts
- Minikube provides default StorageClass

**Implementation**:
```yaml
# PersistentVolumeClaim
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: backend-sqlite-pvc
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 1Gi
```

**Volume Mount**:
```yaml
volumeMounts:
  - name: sqlite-data
    mountPath: /app/data
```

### 5. Secrets Management

**Decision**: Kubernetes Secrets (resolved in spec Q3)

**Rationale**:
- Standard Kubernetes pattern
- Base64 encoded storage
- Mounted as environment variables
- Easy to template in Helm

**Secrets Required**:
| Secret | Keys | Service |
|--------|------|---------|
| backend-secrets | JWT_SECRET_KEY, SMTP_USER, SMTP_PASS | backend |
| chatbot-secrets | OPENROUTER_API_KEY | chatbot |

**Implementation**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: backend-secrets
type: Opaque
stringData:
  JWT_SECRET_KEY: "{{ .Values.secrets.jwtSecretKey }}"
```

### 6. Health Check Patterns

**Decision**: Liveness and Readiness probes for all services

**Rationale**:
- Constitution mandates health checks
- Kubernetes uses probes for pod lifecycle
- Enables rolling updates without downtime

**Endpoints**:
| Service | Health Endpoint | Protocol |
|---------|-----------------|----------|
| Frontend | / (Next.js default) | HTTP |
| Backend | /api/health | HTTP |
| Chatbot | /health | HTTP |

**Probe Configuration**:
```yaml
livenessProbe:
  httpGet:
    path: /api/health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /api/health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

### 7. Resource Management

**Decision**: Standard resource requests/limits for local dev

**Rationale**:
- Prevents resource starvation
- Ensures fair scheduling
- Fits within Minikube constraints (4GB RAM, 2 CPUs)

**Allocation** (per service):
- CPU Request: 250m (0.25 cores)
- CPU Limit: 500m (0.5 cores)
- Memory Request: 256Mi
- Memory Limit: 512Mi

**Total Stack**: 750m CPU, 768Mi memory (requests)

### 8. External Access Strategy

**Decision**: NodePort for frontend only

**Rationale**:
- Simple external access without Ingress controller
- Backend/Chatbot are internal-only (ClusterIP)
- Sufficient for local development

**Port Assignment**:
- Frontend: NodePort 30080 (maps to container 3000)
- Backend: ClusterIP only (internal 8000)
- Chatbot: ClusterIP only (internal 8001)

### 9. AI DevOps Tools

**Decision**: kubectl-ai for K8s, Gordon for Docker

**Rationale**:
- Constitution requires AI-first engineering
- kubectl-ai: Natural language queries for cluster state
- Gordon: Docker troubleshooting assistance

**Usage Examples**:
```bash
# kubectl-ai
kubectl-ai "show me all pods in lumina namespace"
kubectl-ai "why is my backend pod failing?"

# Gordon
gordon "help me debug this Dockerfile"
gordon "optimize my image size"
```

## Dependencies Verified

| Tool | Version | Status |
|------|---------|--------|
| Docker | 24+ | Required |
| Minikube | 1.32+ | Required |
| kubectl | 1.28+ | Required |
| Helm | 3.14+ | Required |
| kubectl-ai | latest | Optional (P3) |
| Gordon | latest | Optional (P3) |

## No Further Research Required

All technical decisions align with:
- User selections from clarification (Q1-Q3)
- Constitution Phase IV standards
- Standard Kubernetes best practices

Ready for Phase 1: data-model.md generation.
