# TriSLA Helm Chart

Helm chart for full TriSLA deployment on Kubernetes.

Initial Public Release alignment: v1.0.0.

## NASP Deployment

The canonical values file for NASP deployment is `values-nasp.yaml`.

```bash
cd ~/gtp5g/trisla

helm upgrade --install trisla ./helm/trisla \
  --namespace trisla \
  --create-namespace \
  --values ./helm/trisla/values-nasp.yaml \
  --wait \
  --timeout 15m
```

## Canonical Values File

For NASP: `helm/trisla/values-nasp.yaml`

This values file is used for real-environment deployment and includes:

- NASP network settings;
- domain controller endpoints (RAN, Transport, Core);
- production-oriented runtime parameters.

## Important Values

### Network Configuration

- `network.interface`: primary network interface (example: `my5g`)
- `network.nodeIP`: node IP used for runtime integration
- `network.gateway`: default gateway

### Production Settings

- `production.enabled`: `true`
- `production.simulationMode`: `false` (real execution path)
- `production.useRealServices`: `true`
- `production.executeRealActions`: `true`

### NASP Endpoints

- `naspAdapter.naspEndpoints.ran`: RAN controller endpoint
- `naspAdapter.naspEndpoints.core_upf`: Core/UPF endpoint
- `naspAdapter.naspEndpoints.transport`: Transport controller endpoint

## Validation

```bash
helm lint ./helm/trisla

helm template trisla ./helm/trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --debug
```

## Post-Deployment Verification

```bash
kubectl get pods -n trisla
kubectl get svc -n trisla
helm status trisla -n trisla
```

