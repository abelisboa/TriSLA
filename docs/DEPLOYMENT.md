# Deployment (Public Guide)

This guide describes a reproducible deployment flow for TriSLA in a generic Kubernetes environment.

## Prerequisites
- Kubernetes cluster (single-node or multi-node)
- Helm 3
- Access to GHCR images (public images under `ghcr.io/abelisboa`)
- Ingress/NodePort strategy for exposing the Portal (optional)

## Recommended deployment order
1. Observability stack (Prometheus / optional Grafana / OTEL collector)
2. Kafka (event backbone)
3. Besu (if on-chain governance is enabled)
4. Core TriSLA services:
   - SEM-CSMF
   - ML-NSMF
   - Decision Engine
   - NASP Adapter
   - SLA-Agent Layer
   - BC-NSSMF (if enabled)
5. Portal:
   - Portal Backend
   - Portal Frontend

## Helm quickstart (example)
> Adjust namespace, values files, and service exposure according to your cluster policy.

```bash
kubectl create namespace trisla

# Install TriSLA core
helm upgrade --install trisla ./helm/trisla -n trisla -f ./helm/trisla/values.yaml

# Install Portal (if separated)
helm upgrade --install trisla-portal ./helm/trisla-portal -n trisla -f ./helm/trisla-portal/values.yaml
```

## Post-deploy validation
- All pods in Running state
- Health endpoints responding (SEM/ML/Decision/Portal)
- Kafka topic readiness
- Prometheus can query expected signals

## Common failure modes
- **Image pull authorization (GHCR):** verify imagePullSecrets if your cluster requires it
- **Empty Prometheus queries:** verify scrape interval and query window compatibility
- **Portal cannot reach backend:** verify frontend base URL configuration
