# Tasks: Local Kubernetes Deployment

**Input**: Design documents from `/specs/011-k8s-local-deploy/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/helm-values.schema.json

**Tests**: Not required for this feature (infrastructure/deployment focused)

**Organization**: Tasks are grouped by implementation phase matching user stories:
- Phase 1 (US1): Docker Containerization
- Phase 2 (US2): Helm Charts & Deployment
- Phase 3 (US3/US4): Verification & AI Tools

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Docker Containerization (User Story 1 - P1) 🎯 MVP

**Goal**: Build Docker container images for all three services

**Independent Test**: Run `docker build` for each service and verify images start correctly

**Acceptance**: All three container images build successfully and respond to health checks

### Frontend Containerization

- [x] T001 [P] [US1] Create .dockerignore for frontend in frontend/.dockerignore
  - **Acceptance**: File excludes node_modules, .next, .git, *.log, .env*

- [x] T002 [P] [US1] Create multi-stage Dockerfile for frontend in frontend/Dockerfile
  - **Acceptance**: Dockerfile has 3 stages (deps, build, runtime), exposes port 3000, runs as non-root user
  - **Reference**: FR-001, FR-004, FR-005

- [x] T003 [US1] Build and verify frontend image with `docker build -t lumina-frontend:latest ./frontend`
  - **Acceptance**: Image builds in < 5 minutes, size < 500MB, container starts and serves on port 3000

### Backend Containerization

- [x] T004 [P] [US1] Create .dockerignore for backend in api/.dockerignore
  - **Acceptance**: File excludes __pycache__, .venv, *.pyc, .git, .env*, data/

- [x] T005 [P] [US1] Update Dockerfile for backend (K8s-ready) in api/Dockerfile
  - **Acceptance**: Uses multi-stage build with UV, exposes port 8000 (not 7860), runs as non-root, includes health check
  - **Reference**: FR-002, FR-004, FR-005

- [x] T006 [US1] Build and verify backend image with `docker build -t lumina-backend:latest ./api`
  - **Acceptance**: Image builds successfully, size < 500MB, container starts and /api/health returns 200

### Chatbot Containerization

- [x] T007 [P] [US1] Verify/update .dockerignore for chatbot in chatbot/.dockerignore
  - **Acceptance**: File excludes __pycache__, .venv, *.pyc, .git, .env*

- [x] T008 [P] [US1] Verify chatbot Dockerfile is K8s-ready in chatbot/Dockerfile
  - **Acceptance**: Already multi-stage, exposes port 8001, runs as non-root, has health check (verify or update)
  - **Reference**: FR-003, FR-004, FR-005

- [x] T009 [US1] Build and verify chatbot image with `docker build -t lumina-chatbot:latest ./chatbot`
  - **Acceptance**: Image builds successfully, size < 500MB, container starts and /health returns 200

**🔲 CHECKPOINT 1**: All 3 images build and start successfully
- Run: `docker images | grep lumina` (shows 3 images, each < 500MB)
- Run: `docker run -d -p 3000:3000 lumina-frontend:latest` (serves web app)
- Run: `docker run -d -p 8000:8000 lumina-backend:latest` (health check passes)
- Run: `docker run -d -p 8001:8001 lumina-chatbot:latest` (health check passes)

---

## Phase 2: Helm Charts (User Story 2 - P2)

**Goal**: Create Helm charts for deploying all services to Kubernetes

**Independent Test**: Run `helm template` to verify chart renders correctly

**Acceptance**: Helm charts deploy all services to Minikube with working inter-service communication

### Umbrella Chart Structure

- [x] T010 [US2] Create umbrella chart structure in helm/lumina-todo/
  - **Acceptance**: Creates Chart.yaml, values.yaml, charts/ directory
  - **Reference**: FR-006

- [x] T011 [US2] Create umbrella Chart.yaml in helm/lumina-todo/Chart.yaml
  - **Acceptance**: Defines name, version, appVersion, dependencies on subcharts
  - **Reference**: FR-006

- [x] T012 [US2] Create umbrella values.yaml in helm/lumina-todo/values.yaml
  - **Acceptance**: Contains global values and subchart value overrides
  - **Reference**: FR-007, FR-020

### Frontend Subchart

- [x] T013 [P] [US2] Create frontend subchart structure in helm/lumina-todo/charts/frontend/
  - **Acceptance**: Creates Chart.yaml, values.yaml, templates/ directory

- [x] T014 [P] [US2] Create frontend _helpers.tpl in helm/lumina-todo/charts/frontend/templates/_helpers.tpl
  - **Acceptance**: Defines common labels, selectors, and name helpers
  - **Reference**: FR-010

- [x] T015 [P] [US2] Create frontend Deployment in helm/lumina-todo/charts/frontend/templates/deployment.yaml
  - **Acceptance**: 1 replica, port 3000, resource limits (250m/500m CPU, 256Mi/512Mi memory), liveness/readiness probes
  - **Reference**: FR-019

- [x] T016 [P] [US2] Create frontend Service in helm/lumina-todo/charts/frontend/templates/service.yaml
  - **Acceptance**: NodePort type, port 3000, nodePort 30080
  - **Reference**: FR-012

- [x] T017 [P] [US2] Create frontend ConfigMap in helm/lumina-todo/charts/frontend/templates/configmap.yaml
  - **Acceptance**: Contains NEXT_PUBLIC_API_URL pointing to backend DNS
  - **Reference**: FR-013

- [x] T018 [US2] Create frontend values.yaml in helm/lumina-todo/charts/frontend/values.yaml
  - **Acceptance**: Configurable image, replicas, resources, service type, nodePort

### Backend Subchart

- [x] T019 [P] [US2] Create backend subchart structure in helm/lumina-todo/charts/backend/
  - **Acceptance**: Creates Chart.yaml, values.yaml, templates/ directory

- [x] T020 [P] [US2] Create backend _helpers.tpl in helm/lumina-todo/charts/backend/templates/_helpers.tpl
  - **Acceptance**: Defines common labels, selectors, and name helpers

- [x] T021 [P] [US2] Create backend Deployment in helm/lumina-todo/charts/backend/templates/deployment.yaml
  - **Acceptance**: 1 replica (fixed for SQLite), port 8000, resource limits, probes, volume mounts for PVC
  - **Reference**: FR-015, FR-019

- [x] T022 [P] [US2] Create backend Service in helm/lumina-todo/charts/backend/templates/service.yaml
  - **Acceptance**: ClusterIP type, port 8000
  - **Reference**: FR-012

- [x] T023 [P] [US2] Create backend ConfigMap in helm/lumina-todo/charts/backend/templates/configmap.yaml
  - **Acceptance**: Contains DATABASE_URL, CHATBOT_URL (DNS), CORS_ORIGINS, ENVIRONMENT
  - **Reference**: FR-013

- [x] T024 [P] [US2] Create backend Secret template in helm/lumina-todo/charts/backend/templates/secret.yaml
  - **Acceptance**: Template for JWT_SECRET_KEY, SMTP_USER, SMTP_PASS
  - **Reference**: FR-016, FR-017, FR-018

- [x] T025 [P] [US2] Create backend PVC in helm/lumina-todo/charts/backend/templates/pvc.yaml
  - **Acceptance**: 1Gi storage, ReadWriteOnce, standard StorageClass
  - **Reference**: FR-009

- [x] T026 [US2] Create backend values.yaml in helm/lumina-todo/charts/backend/values.yaml
  - **Acceptance**: Configurable image, resources, secrets placeholders, persistence settings

### Chatbot Subchart

- [x] T027 [P] [US2] Create chatbot subchart structure in helm/lumina-todo/charts/chatbot/
  - **Acceptance**: Creates Chart.yaml, values.yaml, templates/ directory

- [x] T028 [P] [US2] Create chatbot _helpers.tpl in helm/lumina-todo/charts/chatbot/templates/_helpers.tpl
  - **Acceptance**: Defines common labels, selectors, and name helpers

- [x] T029 [P] [US2] Create chatbot Deployment in helm/lumina-todo/charts/chatbot/templates/deployment.yaml
  - **Acceptance**: 1 replica, port 8001, resource limits, probes
  - **Reference**: FR-019

- [x] T030 [P] [US2] Create chatbot Service in helm/lumina-todo/charts/chatbot/templates/service.yaml
  - **Acceptance**: ClusterIP type, port 8001
  - **Reference**: FR-012

- [x] T031 [P] [US2] Create chatbot ConfigMap in helm/lumina-todo/charts/chatbot/templates/configmap.yaml
  - **Acceptance**: Contains MCP_SERVER_PORT, MCP_SERVER_HOST, BACKEND_URL (DNS), ENVIRONMENT
  - **Reference**: FR-013

- [x] T032 [P] [US2] Create chatbot Secret template in helm/lumina-todo/charts/chatbot/templates/secret.yaml
  - **Acceptance**: Template for OPENROUTER_API_KEY
  - **Reference**: FR-016, FR-017, FR-018

- [x] T033 [US2] Create chatbot values.yaml in helm/lumina-todo/charts/chatbot/values.yaml
  - **Acceptance**: Configurable image, resources, secrets placeholders

### Chart Validation

- [x] T034 [US2] Validate Helm charts with `helm template lumina-todo ./helm/lumina-todo`
  - **Acceptance**: All templates render without errors, no YAML syntax issues

**🔲 CHECKPOINT 2**: Helm charts render correctly
- Run: `helm lint ./helm/lumina-todo` (no errors)
- Run: `helm template lumina-todo ./helm/lumina-todo` (renders all resources)

---

## Phase 3: Minikube Deployment (User Story 2 continued)

**Goal**: Deploy all services to local Minikube cluster

**Independent Test**: All pods reach Running state, services accessible

**Acceptance**: Full stack running on Minikube with inter-service communication working

### Minikube Setup

- [x] T035 [US2] Start Minikube with adequate resources: `minikube start --memory=4096 --cpus=2`
  - **Acceptance**: Minikube status shows Running for host, kubelet, apiserver

- [x] T036 [US2] Configure Docker to use Minikube daemon: `eval $(minikube docker-env)`
  - **Acceptance**: `docker images` shows Minikube's image cache

- [x] T037 [US2] Build all images in Minikube Docker context
  - **Acceptance**: All 3 lumina images visible in `docker images`

### Namespace and Secrets

- [x] T038 [US2] Create lumina namespace: `kubectl create namespace lumina`
  - **Acceptance**: `kubectl get namespaces` shows lumina

- [x] T039 [US2] Create secrets-values.yaml (local only, DO NOT COMMIT)
  - **Acceptance**: File contains backend.secrets.jwtSecretKey, backend.secrets.smtpUser, backend.secrets.smtpPass, chatbot.secrets.openrouterApiKey
  - **Reference**: FR-016

### Helm Deployment

- [x] T040 [US2] Install Helm charts: `helm install lumina-todo ./helm/lumina-todo -n lumina -f secrets-values.yaml`
  - **Acceptance**: Helm reports successful installation

- [x] T041 [US2] Wait for pods to be ready: `kubectl wait --for=condition=ready pod -l app.kubernetes.io/part-of=lumina-todo -n lumina --timeout=120s`
  - **Acceptance**: All pods reach Ready state within 2 minutes
  - **Reference**: SC-003

- [x] T042 [US2] Verify all resources created: `kubectl get all -n lumina`
  - **Acceptance**: Shows 3 deployments, 3 services, 3 pods all in desired state

**🔲 CHECKPOINT 3**: All services deployed and running
- Run: `kubectl get pods -n lumina` (all 3 pods Running)
- Run: `kubectl get svc -n lumina` (shows frontend NodePort, backend/chatbot ClusterIP)
- Run: `kubectl get pvc -n lumina` (PVC Bound)
- Run: `kubectl get secrets -n lumina` (secrets created)

---

## Phase 4: Verification & Testing (User Stories 2, 3, 4)

**Goal**: Verify all services work correctly and document operations

**Independent Test**: End-to-end verification of deployment

**Acceptance**: All success criteria from spec.md validated

### Service Health Verification (US2)

- [x] T043 [US2] Verify frontend accessible via NodePort
  - **Acceptance**: `curl http://$(minikube ip):30080` returns HTML
  - **Reference**: SC-004

- [x] T044 [US2] Verify backend health check
  - **Acceptance**: `kubectl exec -n lumina deploy/backend -- curl -s localhost:8000/api/health` returns OK
  - **Reference**: SC-005

- [x] T045 [US2] Verify chatbot health check
  - **Acceptance**: `kubectl exec -n lumina deploy/chatbot -- curl -s localhost:8001/health` returns OK
  - **Reference**: SC-006

### Inter-Service Communication (US2)

- [x] T046 [US2] Verify frontend can reach backend via K8s DNS
  - **Acceptance**: `kubectl exec -n lumina deploy/frontend -- wget -qO- backend-service.lumina.svc.cluster.local:8000/api/health` succeeds
  - **Reference**: FR-013

- [x] T047 [US2] Verify backend can reach chatbot via K8s DNS
  - **Acceptance**: `kubectl exec -n lumina deploy/backend -- curl -s chatbot-service.lumina.svc.cluster.local:8001/health` succeeds
  - **Reference**: FR-013

### AI-Assisted Operations (US3)

- [x] T048 [P] [US3] Verify kubectl-ai installation and test basic query
  - **Acceptance**: `kubectl-ai "show pods in lumina namespace"` returns pod information (or document if not installed)
  - **Reference**: FR-022

- [x] T049 [P] [US3] Verify Gordon installation and test Docker query
  - **Acceptance**: `gordon "list lumina images"` returns image information (or document if not installed)
  - **Reference**: FR-023

### Lifecycle Operations (US4)

- [x] T050 [US4] Test Helm upgrade operation
  - **Acceptance**: `helm upgrade lumina-todo ./helm/lumina-todo -n lumina` succeeds without downtime
  - **Reference**: SC-010

- [x] T051 [US4] Test Helm rollback operation
  - **Acceptance**: `helm rollback lumina-todo 1 -n lumina` restores previous revision
  - **Reference**: US4 acceptance scenario 2

- [x] T052 [US4] Document uninstall procedure (DO NOT EXECUTE)
  - **Acceptance**: Document `helm uninstall lumina-todo -n lumina && kubectl delete namespace lumina` in quickstart.md
  - **Reference**: US4 acceptance scenario 3

**🔲 CHECKPOINT 4**: All verification tests pass
- All health checks pass
- Inter-service DNS resolution works
- AI tools documented/verified
- Lifecycle operations tested

---

## Phase 5: Documentation & Polish

**Purpose**: Finalize documentation and cleanup

- [x] T053 [P] Update quickstart.md with any discovered issues or tips
  - **Acceptance**: quickstart.md reflects actual deployment experience

- [x] T054 [P] Add .gitignore entries for secrets-values.yaml
  - **Acceptance**: `secrets-values.yaml` pattern added to .gitignore

- [x] T055 Validate full deployment flow from scratch using quickstart.md
  - **Acceptance**: Fresh deployment following quickstart.md succeeds in < 15 minutes
  - **Reference**: SC-007

- [x] T056 Create final verification report documenting all success criteria
  - **Acceptance**: Report shows PASS/FAIL for all 10 success criteria (SC-001 through SC-010)

**🔲 FINAL CHECKPOINT**: Phase IV Local Kubernetes Deployment complete
- All 10 success criteria documented as PASS
- All functional requirements (FR-001 through FR-023) implemented
- Documentation complete and validated

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Docker)     → No dependencies
    ↓
Phase 2 (Helm)       → Depends on Phase 1 images
    ↓
Phase 3 (Deploy)     → Depends on Phase 2 charts
    ↓
Phase 4 (Verify)     → Depends on Phase 3 deployment
    ↓
Phase 5 (Polish)     → Depends on Phase 4 verification
```

### Parallel Opportunities

**Phase 1 - Can run in parallel:**
- T001, T004, T007 (all .dockerignore files)
- T002, T005, T008 (all Dockerfiles)

**Phase 2 - Can run in parallel:**
- T013-T018 (frontend subchart)
- T019-T026 (backend subchart)
- T027-T033 (chatbot subchart)

**Phase 4 - Can run in parallel:**
- T048, T049 (AI tools verification)

### Task Count Summary

| Phase | Tasks | Parallel Tasks | Sequential Tasks |
|-------|-------|----------------|------------------|
| Phase 1 (Docker) | 9 | 6 | 3 |
| Phase 2 (Helm) | 25 | 20 | 5 |
| Phase 3 (Deploy) | 8 | 0 | 8 |
| Phase 4 (Verify) | 10 | 2 | 8 |
| Phase 5 (Polish) | 4 | 2 | 2 |
| **Total** | **56** | **30** | **26** |

---

## Implementation Strategy

### MVP (User Story 1 Only)

1. Complete Phase 1 (T001-T009)
2. Verify all 3 images build and run
3. **STOP**: Docker containerization complete, can deploy manually

### Full Deployment (User Stories 1 + 2)

1. Complete Phase 1 + Phase 2 + Phase 3
2. Verify Minikube deployment works
3. **STOP**: Full K8s deployment functional

### Complete Feature (All User Stories)

1. Complete all phases
2. All verification tests pass
3. Documentation validated
4. Ready for production-like local development

---

## Notes

- All tasks are 15-30 minutes each
- [P] tasks can run in parallel (different files, no dependencies)
- [US#] labels map tasks to user stories for traceability
- Checkpoint after each phase for human review
- DO NOT commit secrets-values.yaml to git
- Minikube must be running for Phase 3+
