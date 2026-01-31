# TriSLA Deployment Guide

## Prerequisites

- Kubernetes 1.26+
- Helm 3.x
- kubectl configured
- Container registry access (ghcr.io)

## Quick Start

```bash
# Clone repository
git clone https://github.com/abelisboa/TriSLA.git
cd TriSLA

# Create namespace
kubectl create namespace trisla

# Create registry secret (if needed)
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=YOUR_USERNAME \
  --docker-password=YOUR_TOKEN \
  -n trisla

# Install TriSLA
helm install trisla ./helm/trisla -n trisla

# Verify deployment
kubectl get pods -n trisla
```

## Configuration

### values.yaml

Key configuration options:

```yaml
global:
  imageRegistry: ghcr.io/abelisboa

# Enable/disable components
semCsmf:
  enabled: true
  image:
    tag: v3.10.0

mlNsmf:
  enabled: true
  
decisionEngine:
  enabled: true
  
bcNssmf:
  enabled: true

besu:
  enabled: true
  
kafka:
  enabled: true
```

## Accessing the Portal

```bash
# Port forward
kubectl port-forward svc/trisla-ui-dashboard 8080:80 -n trisla

# Open browser
open http://localhost:8080
```

## Verifying Installation

```bash
# Check all pods are running
kubectl get pods -n trisla

# Check services
kubectl get svc -n trisla

# Test health endpoints
kubectl exec -n trisla deploy/trisla-decision-engine -- \
  curl -s http://localhost:8082/health
```

## Image Versions

All images for v3.10.0 are available at:

`ghcr.io/abelisboa/trisla-{component}:v3.10.0`
