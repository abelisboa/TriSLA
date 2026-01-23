# TriSLA Installation Guide

## Prerequisites

### Kubernetes Cluster

- Kubernetes version 1.20 or higher
- kubectl configured to access the cluster
- Sufficient resources:
  - Minimum 4 CPU cores
  - Minimum 8GB RAM
  - Storage for persistent volumes (if required)

### Container Registry Access

TriSLA images are hosted on GitHub Container Registry (ghcr.io).

**Authentication Required:**



Or using podman (if Docker is emulated):



### Helm

Helm 3.x is required for deployment:

Downloading https://get.helm.sh/helm-v3.20.0-linux-amd64.tar.gz
Verifying checksum... Done.
Preparing to install helm into /usr/local/bin
Failed to install helm
	For support, go to https://github.com/helm/helm.

## Namespace Setup

Create the namespace for TriSLA:



## Registry Configuration

Ensure your Kubernetes cluster can pull images from ghcr.io. You may need to create a secret:



Then configure imagePullSecrets in your Helm values or deployment manifests.

## Next Steps

After completing prerequisites, proceed to [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions.
