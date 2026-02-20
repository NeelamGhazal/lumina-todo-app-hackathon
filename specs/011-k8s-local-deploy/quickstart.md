# Quickstart: Local Kubernetes Deployment

**Feature**: 011-k8s-local-deploy
**Date**: 2026-02-20
**Time to Deploy**: ~15 minutes

## Prerequisites

Ensure the following tools are installed:

| Tool | Version | Check Command |
|------|---------|---------------|
| Docker | 24+ | `docker --version` |
| Minikube | 1.32+ | `minikube version` |
| kubectl | 1.28+ | `kubectl version --client` |
| Helm | 3.14+ | `helm version` |

Optional AI tools:
- kubectl-ai: `kubectl-ai --version`
- Gordon: `gordon --version`

## Step 1: Start Minikube

```bash
# Start Minikube with recommended resources
minikube start --memory=4096 --cpus=2 --driver=docker

# Verify cluster is running
minikube status
```

Expected output:
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

## Step 2: Configure Docker Environment

Build images directly in Minikube's Docker daemon:

```bash
# Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)

# Verify connection
docker images
```

## Step 3: Build Container Images

Build all three service images:

```bash
# Navigate to project root
cd /path/to/evolution-todo

# Build frontend
docker build -t lumina-frontend:latest ./frontend

# Build backend
docker build -t lumina-backend:latest ./api

# Build chatbot
docker build -t lumina-chatbot:latest ./chatbot

# Verify images are available
docker images | grep lumina
```

Expected output:
```
lumina-frontend   latest   abc123   < 500MB
lumina-backend    latest   def456   < 500MB
lumina-chatbot    latest   ghi789   < 500MB
```

## Step 4: Create Namespace

```bash
kubectl create namespace lumina

# Verify namespace
kubectl get namespaces | grep lumina
```

## Step 5: Create Secrets

Create secrets file (DO NOT commit this file):

```bash
# Create secrets values file
cat > secrets-values.yaml << 'EOF'
backend:
  secrets:
    jwtSecretKey: "your-secure-jwt-secret-key-here"
    smtpUser: "your-email@gmail.com"
    smtpPass: "your-app-password"

chatbot:
  secrets:
    openrouterApiKey: "sk-or-your-api-key"
EOF
```

## Step 6: Deploy with Helm

```bash
# Install the umbrella chart
helm install lumina-todo ./helm/lumina-todo \
  --namespace lumina \
  -f secrets-values.yaml

# Watch pods start up
kubectl get pods -n lumina -w
```

Wait for all pods to show `Running` status (usually 1-2 minutes).

## Step 7: Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n lumina

# Check all services are created
kubectl get svc -n lumina

# Check PVC is bound
kubectl get pvc -n lumina

# Check secrets exist
kubectl get secrets -n lumina
```

Expected pod status:
```
NAME                        READY   STATUS    RESTARTS   AGE
frontend-xxxxxxx-xxxxx      1/1     Running   0          2m
backend-xxxxxxx-xxxxx       1/1     Running   0          2m
chatbot-xxxxxxx-xxxxx       1/1     Running   0          2m
```

## Step 8: Access the Application

### Option A: Minikube Service Tunnel

```bash
# Open frontend in browser
minikube service frontend-service -n lumina
```

### Option B: Direct NodePort Access

```bash
# Get Minikube IP
minikube ip

# Access frontend at http://<minikube-ip>:30080
curl http://$(minikube ip):30080
```

### Option C: Port Forward (for debugging)

```bash
# Forward frontend locally
kubectl port-forward svc/frontend-service 3000:3000 -n lumina

# Access at http://localhost:3000
```

## Step 9: Verify Service Communication

```bash
# Test backend health
kubectl exec -n lumina deploy/backend -- curl -s localhost:8000/api/health

# Test chatbot health
kubectl exec -n lumina deploy/chatbot -- curl -s localhost:8001/health

# Test frontend can reach backend (from within cluster)
kubectl exec -n lumina deploy/frontend -- wget -qO- backend-service.lumina.svc.cluster.local:8000/api/health
```

## Common Operations

### View Logs

```bash
# Frontend logs
kubectl logs -n lumina -l app.kubernetes.io/name=frontend -f

# Backend logs
kubectl logs -n lumina -l app.kubernetes.io/name=backend -f

# Chatbot logs
kubectl logs -n lumina -l app.kubernetes.io/name=chatbot -f
```

### Update Configuration

```bash
# Update Helm values
helm upgrade lumina-todo ./helm/lumina-todo \
  --namespace lumina \
  -f secrets-values.yaml
```

### Rollback

```bash
# List revisions
helm history lumina-todo -n lumina

# Rollback to previous version
helm rollback lumina-todo 1 -n lumina
```

### Uninstall

```bash
# Remove all resources
helm uninstall lumina-todo -n lumina

# Delete namespace
kubectl delete namespace lumina

# Stop Minikube (optional)
minikube stop
```

## Known Issues & Tips

### WSL Users
If running on Windows Subsystem for Linux (WSL), direct access to `$(minikube ip):30080` may not work due to network bridging. Use one of these alternatives:

```bash
# Option 1: Use minikube tunnel
minikube service frontend-service -n lumina

# Option 2: Port forward
kubectl port-forward svc/frontend-service 3000:3000 -n lumina

# Option 3: Test from within cluster
kubectl run curl-test --image=curlimages/curl --rm -it --restart=Never \
  -n lumina -- curl -s http://frontend-service:3000/
```

### Backend Async SQLite
The backend uses SQLAlchemy's async engine with `aiosqlite`. The DATABASE_URL must use the `sqlite+aiosqlite://` prefix, which is pre-configured in the Helm values.

### Chatbot Container Has No curl
The chatbot container is minimal and doesn't include curl. Test health from outside the pod:

```bash
kubectl run curl-test --image=curlimages/curl --rm -it --restart=Never \
  -n lumina -- curl -s http://chatbot-service:8001/health
```

### AI Tools Setup
- **kubectl-ai**: Requires `OPENAI_API_KEY` environment variable
- **Gordon**: Optional, install from https://github.com/ajitid/gordon

## Troubleshooting

### Pods Stuck in Pending

```bash
# Check events
kubectl describe pod <pod-name> -n lumina

# Check resource availability
kubectl top nodes
```

**Solution**: Increase Minikube resources or reduce pod requests.

### Image Pull Errors

```bash
# Verify images exist in Minikube's Docker
eval $(minikube docker-env)
docker images | grep lumina
```

**Solution**: Rebuild images with `eval $(minikube docker-env)` active.

### CrashLoopBackOff

```bash
# Check logs
kubectl logs <pod-name> -n lumina --previous

# Check environment variables
kubectl describe pod <pod-name> -n lumina
```

**Solution**: Check secrets are correctly configured.

### Service Unreachable

```bash
# Check endpoints
kubectl get endpoints -n lumina

# Test DNS resolution
kubectl run -it --rm debug --image=busybox -n lumina -- nslookup backend-service.lumina.svc.cluster.local
```

## AI-Assisted Operations

### kubectl-ai

```bash
# Natural language cluster queries
kubectl-ai "show me pods that are not running in lumina namespace"
kubectl-ai "what's using the most memory?"
kubectl-ai "why is my backend pod failing?"
```

### Gordon

```bash
# Docker troubleshooting
gordon "help me optimize my Dockerfile"
gordon "why is my image so large?"
gordon "debug container startup issues"
```

## Success Criteria Checklist

Run these verification commands after deployment:

```bash
# SC-001: Docker images built
docker images | grep lumina

# SC-002: Helm charts lint successfully
helm lint ./helm/lumina-todo

# SC-003: Pods ready within 2 minutes
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=lumina-todo \
  -n lumina --timeout=120s

# SC-004: Frontend accessible
kubectl run curl-test --image=curlimages/curl --rm -it --restart=Never \
  -n lumina -- curl -s http://frontend-service:3000/

# SC-005: Backend health
kubectl exec -n lumina deploy/lumina-todo-backend -- curl -s localhost:8000/api/health

# SC-006: Chatbot health
kubectl run curl-test2 --image=curlimages/curl --rm -it --restart=Never \
  -n lumina -- curl -s http://chatbot-service:8001/health

# SC-007: Fresh deployment < 15 minutes (follow this guide)

# SC-008: Inter-service DNS
kubectl run curl-test3 --image=curlimages/curl --rm -it --restart=Never \
  -n lumina -- curl -s http://backend-service.lumina.svc.cluster.local:8000/api/health

# SC-009: PVC bound
kubectl get pvc -n lumina

# SC-010: Helm upgrade/rollback
helm upgrade lumina-todo ./helm/lumina-todo -n lumina -f secrets-values.yaml
helm rollback lumina-todo 1 -n lumina
```
