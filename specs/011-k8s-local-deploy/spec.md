# Feature Specification: Local Kubernetes Deployment

**Feature Branch**: `011-k8s-local-deploy`
**Created**: 2026-02-20
**Updated**: 2026-02-20 (clarifications resolved)
**Status**: Ready for Planning
**Input**: User description: "Phase IV: Local Kubernetes Deployment for Lumina Todo - Deploy all 3 services (Frontend, Backend, Chatbot) on local Minikube cluster with Docker containerization and Helm charts."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Builds Container Images (Priority: P1)

As a developer, I want to build Docker container images for all three services (frontend, backend, chatbot) so that they can be deployed consistently in any container environment.

**Why this priority**: Container images are the foundation for Kubernetes deployment. Without working Docker images, no deployment is possible.

**Independent Test**: Can be fully tested by running build commands for each service and verifying the resulting images start correctly with Docker.

**Acceptance Scenarios**:

1. **Given** a developer has Docker installed, **When** they build the frontend service, **Then** a working container image is created that serves the web application on port 3000.
2. **Given** a developer has Docker installed, **When** they build the backend service, **Then** a working container image is created that runs the API server on port 8000.
3. **Given** a developer has Docker installed, **When** they build the chatbot service, **Then** a working container image is created that runs the chatbot API on port 8001.
4. **Given** container images are built, **When** a developer runs them individually, **Then** each service starts and responds to health checks.

---

### User Story 2 - Developer Deploys to Local Kubernetes (Priority: P2)

As a developer, I want to deploy all services to a local Minikube cluster using Helm charts so that I can test the full application stack in a Kubernetes environment.

**Why this priority**: After container images are ready, deployment to Kubernetes validates the orchestration and inter-service communication.

**Independent Test**: Can be fully tested by running Helm install commands and verifying all services reach healthy state.

**Acceptance Scenarios**:

1. **Given** Minikube is running and images are available, **When** a developer installs the Helm charts, **Then** all three services are deployed in the `lumina` namespace.
2. **Given** services are deployed, **When** a developer checks service status, **Then** all services show healthy state.
3. **Given** services are running, **When** a developer accesses the frontend via NodePort, **Then** the web application is accessible and functional.
4. **Given** services are running, **When** the frontend calls the backend using Kubernetes DNS (`backend-service.lumina.svc.cluster.local`), **Then** API requests succeed.
5. **Given** services are running, **When** the backend calls the chatbot using Kubernetes DNS (`chatbot-service.lumina.svc.cluster.local`), **Then** chatbot requests succeed.

---

### User Story 3 - Developer Uses AI-Assisted Operations (Priority: P3)

As a developer, I want to use AI-assisted tools (kubectl-ai for Kubernetes, Gordon for Docker) to help troubleshoot and manage the deployment more efficiently.

**Why this priority**: AI tooling enhances developer experience but is not required for core deployment functionality.

**Independent Test**: Can be tested by invoking AI tools for common operations and verifying helpful responses.

**Acceptance Scenarios**:

1. **Given** kubectl-ai is available, **When** a developer asks about cluster status, **Then** kubectl-ai provides accurate information.
2. **Given** Gordon is available, **When** a developer asks for Docker help, **Then** Gordon provides relevant guidance.

---

### User Story 4 - Developer Manages Deployment Lifecycle (Priority: P3)

As a developer, I want to easily update, rollback, and remove deployments so that I can iterate during development.

**Why this priority**: Lifecycle management supports iterative development but builds on core deployment.

**Independent Test**: Can be tested by performing upgrade, rollback, and uninstall operations successfully.

**Acceptance Scenarios**:

1. **Given** services are deployed, **When** a developer updates configuration, **Then** changes are applied without downtime.
2. **Given** an upgrade was applied, **When** a developer needs to rollback, **Then** the previous version is restored.
3. **Given** services are deployed, **When** a developer removes the deployment, **Then** all resources are cleanly removed from the `lumina` namespace.

---

### Edge Cases

- What happens when Minikube runs out of resources (CPU/memory)? → Pods enter Pending state with resource pressure events.
- How does the system handle when one service fails while others succeed? → Partial deployment; failed service shows CrashLoopBackOff, others remain healthy.
- What happens when container builds fail due to missing dependencies? → Build fails with clear error; no image created.
- How does inter-service communication work when services restart? → Kubernetes DNS automatically resolves to new pod IPs; no manual intervention needed.
- What happens when the database storage is not properly configured? → Backend pod fails to start; PVC remains in Pending state if StorageClass unavailable.

## Requirements *(mandatory)*

### Functional Requirements

#### Docker Containerization

- **FR-001**: System MUST provide container configuration for the frontend service that creates a production-ready image exposing port 3000.
- **FR-002**: System MUST provide container configuration for the backend service that creates a production-ready image exposing port 8000.
- **FR-003**: System MUST provide container configuration for the chatbot service that creates a production-ready image exposing port 8001.
- **FR-004**: Container configurations MUST use multi-stage builds to minimize image size.
- **FR-005**: Container images MUST include health check endpoints for orchestration readiness and liveness probes.

#### Helm Charts

- **FR-006**: System MUST provide Helm charts in a `/helm` directory for deploying all services.
- **FR-007**: Helm charts MUST include configurable values for environment settings, resource limits, and replicas.
- **FR-008**: Helm charts MUST define Deployments, Services, ConfigMaps, Secrets, and PersistentVolumeClaims.
- **FR-009**: Helm charts MUST support persistent storage configuration for the SQLite database file used by the backend.
- **FR-010**: Helm charts MUST include appropriate labels and selectors for Kubernetes DNS-based service discovery.

#### Kubernetes Deployment

- **FR-011**: System MUST deploy successfully on Minikube with default configurations in the `lumina` namespace.
- **FR-012**: Services MUST be accessible via ClusterIP services internally and NodePort for external access to frontend.
- **FR-013**: Services MUST communicate using Kubernetes DNS names (e.g., `backend-service.lumina.svc.cluster.local`).
- **FR-014**: System MUST support environment-specific configuration through Helm values files.
- **FR-015**: Backend service MUST run as a single replica to ensure SQLite database integrity.

#### Secrets Management

- **FR-016**: Sensitive configuration (JWT secret, SMTP credentials, API keys) MUST be stored in Kubernetes Secrets.
- **FR-017**: Secrets MUST be mounted as environment variables in the appropriate pods.
- **FR-018**: Helm charts MUST provide templates for creating Secrets with configurable values.

#### Resource Management

- **FR-019**: Each pod MUST have defined resource requests (CPU: 250m, Memory: 256Mi) and limits (CPU: 500m, Memory: 512Mi).
- **FR-020**: Resource configurations MUST be overridable through Helm values.

#### Developer Experience

- **FR-021**: Documentation MUST include step-by-step deployment instructions for Minikube.
- **FR-022**: System SHOULD integrate with kubectl-ai for AI-assisted Kubernetes operations.
- **FR-023**: System SHOULD integrate with Gordon for Docker operations assistance.

### Key Entities

- **Container Image**: A packaged application with all dependencies, ready to run in any container runtime.
- **Helm Chart**: A collection of Kubernetes manifests templated for configurable deployment.
- **Deployment**: A workload resource managing application replicas and rollout strategy.
- **Service**: A network abstraction providing stable DNS endpoint for accessing applications.
- **Secret**: A Kubernetes resource storing sensitive data (passwords, tokens, keys) in base64 encoding.
- **ConfigMap**: A Kubernetes resource storing non-sensitive configuration data.
- **PersistentVolumeClaim**: A request for storage that binds to a PersistentVolume for data persistence.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All three services can be built into container images in under 10 minutes total.
- **SC-002**: Full stack deployment to local cluster completes in under 5 minutes.
- **SC-003**: All services reach healthy state within 2 minutes of deployment.
- **SC-004**: Frontend application is accessible via NodePort and functional after deployment.
- **SC-005**: Backend API responds to requests from within (via ClusterIP) and outside (via NodePort) the cluster.
- **SC-006**: Chatbot service successfully handles requests routed from the backend via Kubernetes DNS.
- **SC-007**: Developer can complete first deployment following documentation within 15 minutes.
- **SC-008**: System supports at least 5 concurrent users in local environment.
- **SC-009**: Container images are less than 500MB each for efficient local development.
- **SC-010**: Upgrade operations complete without service interruption.

## Technical Specifications

### Service Ports

| Service | Container Port | Service Type | NodePort (if applicable) |
|---------|---------------|--------------|--------------------------|
| Frontend | 3000 | NodePort | 30080 |
| Backend | 8000 | ClusterIP | N/A (internal only) |
| Chatbot | 8001 | ClusterIP | N/A (internal only) |

### Kubernetes DNS Names

| Service | Internal DNS Name |
|---------|-------------------|
| Frontend | `frontend-service.lumina.svc.cluster.local` |
| Backend | `backend-service.lumina.svc.cluster.local` |
| Chatbot | `chatbot-service.lumina.svc.cluster.local` |

### Resource Defaults

| Resource | Request | Limit |
|----------|---------|-------|
| CPU | 250m | 500m |
| Memory | 256Mi | 512Mi |

### Secrets Required

| Secret Name | Keys | Used By |
|-------------|------|---------|
| `backend-secrets` | `JWT_SECRET_KEY`, `SMTP_USER`, `SMTP_PASS` | Backend |
| `chatbot-secrets` | `OPENROUTER_API_KEY` (if applicable) | Chatbot |

## Assumptions

- Developer has Docker Desktop or Docker Engine installed and running.
- Developer has Minikube installed with sufficient resources (recommended: 4GB RAM, 2 CPUs).
- Developer has kubectl and Helm CLI tools installed.
- kubectl-ai and Gordon are optional enhancements, not required for core functionality.
- SQLite is acceptable for local development; single backend replica ensures database integrity.
- Container images will be stored locally in Minikube's Docker daemon (no external registry required).
- Existing application code requires no modifications for containerization.
- Minikube's default StorageClass is available for PersistentVolumeClaim provisioning.

## Out of Scope

- Cloud provider deployment (GKE, EKS, AKS).
- Container registry setup (Docker Hub, ECR, GCR).
- CI/CD pipeline integration.
- Horizontal auto-scaling (backend limited to 1 replica due to SQLite).
- Ingress controller configuration (NodePort is sufficient for local).
- Database migration to production databases (PostgreSQL, MySQL).
- SSL/TLS certificate management.
- Monitoring and logging infrastructure (Prometheus, Grafana, ELK).
- Production scaling configurations.
- External secrets management (Vault, AWS Secrets Manager).
