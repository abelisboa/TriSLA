## Reproducibility Setup Guide (Runtime-Faithful)

This guide is aligned with the current SSOT behavior (`apps/*/src`) and Helm
deployment paths.

### 1. Preconditions

- Kubernetes cluster available
- Helm 3.x installed
- `kubectl` context pointing to target cluster
- namespace-level permissions to create/update TriSLA resources

### 2. Deployment (NASP-oriented profile)

```bash
cd ~/gtp5g/trisla_public

helm upgrade --install trisla ./helm/trisla \
  --namespace trisla \
  --create-namespace \
  --values ./helm/trisla/values-nasp.yaml \
  --wait \
  --timeout 15m
```

### 3. Validate chart and rendered manifests

```bash
helm lint ./helm/trisla

helm template trisla ./helm/trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --debug
```

### 4. Post-deploy checks

```bash
kubectl get pods -n trisla
kubectl get svc -n trisla
helm status trisla -n trisla
```

### 5. Runtime endpoint sanity checks

```bash
curl -s http://<portal-backend>/api/v1/health/global
curl -s http://<portal-backend>/api/v1/sla/submit -X POST -H "Content-Type: application/json" -d '{}'
curl -s http://<nasp-adapter>/api/v1/metrics/multidomain
curl -s http://<decision-engine>/health
```

### 6. Reproducibility-critical runtime flags

To reproduce decision/orchestration behavior, control and report:

- `POLICY_GOVERNED_MODE`
- `PRB_RISK_ALPHA`
- `HARD_PRB_REJECT_THRESHOLD`
- `HARD_PRB_RENEGOTIATE_THRESHOLD`
- `GATE_3GPP_ENABLED`
- `CAPACITY_ACCOUNTING_ENABLED`

These parameters directly impact decision boundaries and NSI acceptance behavior.
