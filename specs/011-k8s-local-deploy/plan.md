# Implementation Plan: Local Kubernetes Deployment

**Branch**: `011-k8s-local-deploy` | **Date**: 2026-02-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-k8s-local-deploy/spec.md`

## Summary

Deploy all three Lumina Todo services (Frontend, Backend, Chatbot) to a local Minikube cluster using Docker containerization and Helm charts. Services communicate via Kubernetes DNS, with SQLite persistence on a single backend replica and secrets managed through Kubernetes Secrets.

## Technical Context

**Language/Version**:
- Frontend: Node.js 20 LTS (Next.js 16+, TypeScript 5.x)
- Backend: Python 3.11+ (FastAPI, SQLModel)
- Chatbot: Python 3.13+ (FastAPI, OpenAI Agents SDK, MCP SDK)

**Primary Dependencies**:
- Docker (multi-stage builds)
- Minikube (local Kubernetes)
- Helm 3.x (chart templating)
- kubectl-ai (AI-assisted K8s operations)
- Gordon (AI-assisted Docker operations)

**Storage**: SQLite via PersistentVolumeClaim (backend service only)

**Testing**:
- kubectl get pods (deployment verification)
- Service health checks (liveness/readiness probes)
- curl/httpx for endpoint validation

**Target Platform**: Local Minikube (WSL 2 / Linux)

**Project Type**: Web (multi-service microservices)

**Performance Goals**:
- Build time: < 10 minutes total for all 3 images
- Deployment time: < 5 minutes to healthy state
- Service startup: < 2 minutes to ready
- API latency: < 200ms

**Constraints**:
- Minikube resources: 4GB RAM, 2 CPUs recommended
- Single backend replica (SQLite integrity)
- Container images: < 500MB each
- Local deployment only (no cloud registry)

**Scale/Scope**:
- 3 services (frontend, backend, chatbot)
- 1 namespace (`lumina`)
- 5+ concurrent users supported

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status |
|-----------|-------------|--------|
| I. Spec-Driven | Spec complete with 23 FRs, 10 success criteria | ✅ PASS |
| II. Professional Quality | Multi-stage builds, health checks, resource limits | ✅ PASS |
| IV. Task-Driven | Tasks will reference spec FRs | ✅ PASS |
| VI. AI-First | kubectl-ai and Gordon for AI-assisted ops | ✅ PASS |
| VII. Cloud-Native | Docker builds, Helm charts, K8s resources | ✅ PASS |

**Phase IV Constitution Standards Applied**:
- [x] Multi-stage Docker builds
- [x] Health checks (liveness/readiness) for all services
- [x] Resource limits and requests defined
- [x] Helm charts with proper templating
- [x] ConfigMaps for configuration, Secrets for sensitive data
- [x] Proper labeling and annotations

## Project Structure

### Documentation (this feature)

```text
specs/011-k8s-local-deploy/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (K8s resource models)
├── quickstart.md        # Phase 1 output (deployment guide)
├── contracts/           # Phase 1 output (Helm values schema)
│   └── helm-values.schema.json
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
# Existing services (to be containerized)
frontend/                 # Next.js 16+ application
├── Dockerfile           # NEW: Multi-stage build
├── .dockerignore        # NEW: Exclude node_modules, etc.
└── src/                 # Existing source code

api/                     # FastAPI backend
├── Dockerfile           # EXISTS: Needs update for K8s
├── .dockerignore        # NEW: Exclude venv, etc.
└── app/                 # Existing source code

chatbot/                 # MCP/Agent server
├── Dockerfile           # EXISTS: Already multi-stage
├── .dockerignore        # Verify exists
└── mcp_server/          # Existing source code

# NEW: Helm charts directory
helm/
├── lumina-todo/         # Umbrella chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── charts/
│       ├── frontend/
│       │   ├── Chart.yaml
│       │   ├── values.yaml
│       │   └── templates/
│       │       ├── deployment.yaml
│       │       ├── service.yaml
│       │       ├── configmap.yaml
│       │       └── _helpers.tpl
│       ├── backend/
│       │   ├── Chart.yaml
│       │   ├── values.yaml
│       │   └── templates/
│       │       ├── deployment.yaml
│       │       ├── service.yaml
│       │       ├── configmap.yaml
│       │       ├── secret.yaml
│       │       └── pvc.yaml
│       └── chatbot/
│           ├── Chart.yaml
│           ├── values.yaml
│           └── templates/
│               ├── deployment.yaml
│               ├── service.yaml
│               ├── configmap.yaml
│               └── secret.yaml
```

**Structure Decision**: Umbrella Helm chart (`lumina-todo`) with subcharts for each service enables independent upgrades while supporting coordinated deployment.

## Complexity Tracking

> No violations detected. All architecture follows Phase IV constitution standards.

| Decision | Rationale | Simpler Alternative Rejected |
|----------|-----------|------------------------------|
| Umbrella chart | Simplifies single-command deploy | Individual charts require 3 install commands |
| Single backend replica | SQLite integrity (per spec) | N/A - required by spec |
| NodePort for frontend | Simple external access without Ingress | Ingress adds complexity for local dev |

## Architecture Decisions

### ADR-001: Service Communication via Kubernetes DNS

**Decision**: Services communicate using Kubernetes DNS names (`<service>.lumina.svc.cluster.local`)

**Rationale**:
- Standard Kubernetes pattern
- No manual IP management
- Automatic failover when pods restart
- Selected by user in clarification Q1

**Alternatives Rejected**:
- Hardcoded IPs: Brittle, breaks on pod restart
- Service mesh: Overkill for local development

### ADR-002: Single Backend Replica for SQLite

**Decision**: Backend runs as single replica with PersistentVolumeClaim

**Rationale**:
- SQLite doesn't support concurrent writes from multiple processes
- PVC ensures data persists across pod restarts
- Selected by user in clarification Q2

**Alternatives Rejected**:
- Multiple replicas with PostgreSQL: Out of scope (local SQLite only)
- ReadWriteMany PVC: SQLite still can't handle concurrent writes

### ADR-003: Kubernetes Secrets for Sensitive Data

**Decision**: Store JWT_SECRET_KEY, SMTP credentials, API keys in K8s Secrets

**Rationale**:
- Standard Kubernetes pattern
- Base64 encoded (not encrypted, but separated from ConfigMaps)
- Mounted as environment variables
- Selected by user in clarification Q3

**Alternatives Rejected**:
- Vault/External secrets: Overkill for local development
- ConfigMaps: Inappropriate for sensitive data

## Port Mapping Strategy

| Service | Container Port | K8s Service Type | External Access |
|---------|---------------|------------------|-----------------|
| Frontend | 3000 | NodePort (30080) | http://localhost:30080 |
| Backend | 8000 | ClusterIP | Internal only |
| Chatbot | 8001 | ClusterIP | Internal only |

**Minikube Access**: Use `minikube service frontend-service -n lumina --url` or direct NodePort access.

## Resource Allocation

| Service | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---------|-------------|-----------|----------------|--------------|
| Frontend | 250m | 500m | 256Mi | 512Mi |
| Backend | 250m | 500m | 256Mi | 512Mi |
| Chatbot | 250m | 500m | 256Mi | 512Mi |

**Total**: 750m CPU request, 1500m limit; 768Mi memory request, 1536Mi limit
**Minikube Fit**: Comfortably within 4GB RAM / 2 CPU recommendation

## Implementation Phases

### Phase 1: Docker Containerization (P1)

1. Create frontend Dockerfile (multi-stage: deps → build → runtime)
2. Update backend Dockerfile (adapt from HF Spaces to K8s)
3. Verify chatbot Dockerfile (already multi-stage)
4. Create .dockerignore files for each service
5. Test local builds with `docker build`
6. Verify health check endpoints exist

### Phase 2: Helm Charts (P2)

1. Create umbrella chart structure (`helm/lumina-todo/`)
2. Create frontend subchart (Deployment, Service, ConfigMap)
3. Create backend subchart (Deployment, Service, ConfigMap, Secret, PVC)
4. Create chatbot subchart (Deployment, Service, ConfigMap, Secret)
5. Configure values.yaml with sensible defaults
6. Add _helpers.tpl for common labels

### Phase 3: Minikube Deployment (P2)

1. Start Minikube with adequate resources
2. Configure Minikube to use local Docker images
3. Create lumina namespace
4. Install Helm charts
5. Verify pods reach Running state
6. Test service connectivity

### Phase 4: Verification & AI Tools (P3)

1. Verify frontend accessible via NodePort
2. Test backend health checks
3. Test chatbot endpoint
4. Use kubectl-ai for cluster inspection
5. Use Gordon for Docker troubleshooting
6. Document any issues and fixes

## Success Verification

| Criteria | Verification Command |
|----------|---------------------|
| All pods running | `kubectl get pods -n lumina` |
| Services created | `kubectl get svc -n lumina` |
| Frontend accessible | `curl http://$(minikube ip):30080` |
| Backend health | `kubectl exec -n lumina deploy/backend -- curl localhost:8000/api/health` |
| Chatbot health | `kubectl exec -n lumina deploy/chatbot -- curl localhost:8001/health` |
| PVC bound | `kubectl get pvc -n lumina` |
| Secrets created | `kubectl get secrets -n lumina` |

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Minikube resource exhaustion | Pods stuck in Pending | Start with `--memory=4096 --cpus=2` |
| Image pull failures | Deployment hangs | Use `eval $(minikube docker-env)` to build locally |
| SQLite corruption | Data loss | Single replica + PVC; backup before changes |
| Port conflicts | Service unreachable | Use unique NodePorts; check `netstat` first |

## Next Steps

After plan approval:
1. Run `/sp.tasks` to generate implementation tasks
2. Follow task sequence: Dockerize → Helm → Deploy → Verify
3. Checkpoint after each phase for human review
