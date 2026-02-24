# CI/CD Python App

A simple Flask application demonstrating a complete CI/CD pipeline with GitHub Actions, Docker, Helm, ArgoCD, and Kubernetes.

## Architecture Overview

```text
GitHub Push → GitHub Actions (CI) → Docker Hub → GitHub Actions (CD) → ArgoCD → Kubernetes (Minikube)
```

## Application

A Python Flask API with two endpoints:

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/details` | Returns hostname, IP, timestamp, and status |
| `GET /api/v1/healthz` | Health check endpoint (used by K8s probes) |

The app runs on port **5000**.

## Project Structure

```
├── src/
│   └── app.py                  # Flask application
├── Dockerfile                  # Container image definition (python:3.14-slim)
├── requirements.txt            # Python dependencies (Flask)
├── .github/workflows/
│   └── cicd.yaml               # CI/CD pipeline definition
├── k8s/                        # Raw Kubernetes manifests (for manual deployment)
│   ├── namespace.yaml
│   ├── deployment.yaml
│   └── dockerhub-secret.yaml
├── charts/
│   ├── python-app/             # Helm chart for the application
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── _helpers.tpl
│   │       ├── namespace.yaml
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       ├── ingress.yaml
│   │       └── dockerhub-secret.yaml
│   ├── argocd/                 # ArgoCD Helm values
│   │   └── values.yaml
│   └── github-runners/         # Self-hosted runner config
│       └── runnerdeployment.yaml
├── catalog-info.yaml           # Backstage service catalog entry
└── docs/
    └── index.md                # This file
```

## CI/CD Pipeline

Defined in `.github/workflows/cicd.yaml`, triggered on push to `main` when files in `src/` change.

### CI Job (GitHub-hosted runner)

1. Generates a short commit ID (first 6 chars of SHA)
2. Logs into Docker Hub using repository secrets
3. Builds a multi-arch Docker image (`linux/amd64` + `linux/arm64`)
4. Pushes to `docker.io/mehabadi/test:cicd-app-<commit-id>`

### CD Job (Self-hosted runner)

1. Installs `yq` for YAML manipulation
2. Checks out the repository
3. Updates `charts/python-app/values.yaml` with the new image tag
4. Commits and pushes the change back to git
5. Installs ArgoCD CLI and triggers a sync of the `python-app` application

## Deployment

### Prerequisites

- Minikube (or any Kubernetes cluster)
- Helm 3
- ArgoCD installed in the cluster
- Docker Hub credentials stored as a Kubernetes secret

### Kubernetes Resources

| Resource | Name | Details |
|----------|------|---------|
| Namespace | `cicd-app` | Application namespace |
| Deployment | `python-app` | 1 replica, port 5000 |
| Service | `python-app` | NodePort on 30100 |
| Secret | `docker-registry-secret` | Docker Hub pull credentials (created manually) |
| Ingress | nginx class, path `/` | |

### Manual Deployment (without ArgoCD)

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create Docker Hub secret
kubectl create secret docker-registry docker-registry-secret \
  --namespace=cicd-app \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=<username> \
  --docker-password=<token>

# Deploy with Helm
helm install python-app ./charts/python-app
```

### Access the App

```bash
# Via minikube
minikube service python-app -n cicd-app

# Via port-forward
kubectl port-forward -n cicd-app svc/python-app 8080:5000

# Via NodePort
http://<minikube-ip>:30100/api/v1/details
```

## Backstage Integration

The project includes a `catalog-info.yaml` for registering as a service in [Backstage](https://backstage.io):

- **Name:** cicd-python-app
- **Type:** service
- **Owner:** development
- **Lifecycle:** experimental
