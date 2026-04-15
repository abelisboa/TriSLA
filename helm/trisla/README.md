# TriSLA Helm Chart

Helm chart for full TriSLA deployment on Kubernetes.

## NASP Installation

The canonical values file for NASP deployment is `values-nasp.yaml`:

```bash
cd ~/gtp5g/trisla

# Deploy on NASP
helm upgrade --install trisla ./helm/trisla \
  --namespace trisla \
  --create-namespace \
  --values ./helm/trisla/values-nasp.yaml \
  --wait \
  --timeout 15m
```

## Canonical Values File

**For NASP:** `helm/trisla/values-nasp.yaml`

This is the default file for production deployment in the NASP environment. It contains:
- NASP network settings
- Controller endpoints (RAN, Transport, Core)
- Real production settings
- Production-optimized resources

## Important Values

### Network Configuration
- `network.interface`: Primary network interface (e.g., "my5g")
- `network.nodeIP`: Node1 IP (e.g., "REPLACE_ME")
- `network.gateway`: Default gateway

### Production Settings
- `production.enabled`: true
- `production.simulationMode`: false (⚠️ DO NOT use simulation)
- `production.useRealServices`: true (⚠️ Use REAL services)
- `production.executeRealActions`: true (⚠️ Execute REAL actions)

### NASP Endpoints
- `naspAdapter.naspEndpoints.ran`: RAN controller endpoint
- `naspAdapter.naspEndpoints.core_upf`: UPF endpoint (Core)
- `naspAdapter.naspEndpoints.transport`: Transport controller endpoint

## Validation

```bash
# Chart lint
helm lint ./helm/trisla

# Template with values-nasp.yaml
helm template trisla ./helm/trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --debug
```

## Post-Deployment Verification

```bash
# Check pods
kubectl get pods -n trisla

# Check services
kubectl get svc -n trisla

# Check Helm release status
helm status trisla -n trisla
```

