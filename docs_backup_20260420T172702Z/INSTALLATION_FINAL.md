# TRI-SLA INSTALLATION GUIDE (FINAL)

## 1. Overview

This guide defines one canonical, linear installation flow for TriSLA on Kubernetes with Helm, using only repository evidence from `apps/`, `helm/trisla/`, `docs/deployment/`, and existing scripts.

Scope:
- Deploy core TriSLA services via `helm/trisla`.
- Use `helm/trisla/values-nasp.yaml` as the canonical values file.
- Validate resulting pods/services and key service-to-service links.

## 2. Architecture Summary

Canonical deploy target in this repository is the `helm/trisla` chart with these core services:
- `sem-csmf`, `ml-nsmf`, `decision-engine`, `bc-nssmf`, `sla-agent-layer`, `nasp-adapter`.
- Supporting services in the same chart: `ui-dashboard`, `traffic-exporter`, `kafka`, `besu`.

Service dependency evidence (from deployment templates):
- `decision-engine` -> `ml-nsmf`, `sla-agent-layer`.
- `sla-agent-layer` -> `nasp-adapter`, `bc-nssmf`, `kafka`.
- `nasp-adapter` -> `sem-csmf`, Prometheus URL.
- `bc-nssmf` -> `besu` RPC, wallet secret/configmap.
- `sem-csmf` and `ml-nsmf` -> `kafka`.

## 3. Prerequisites

### Required Tooling
- Kubernetes cluster access (`kubectl cluster-info` must work).
- Helm 3.x (`helm version`).
- `kubectl` client.
- Access to GHCR images (`ghcr.io/abelisboa/*`) or chart-renderable image credentials.

### Minimum Infra Inputs
- Namespace: `trisla`.
- Valid `helm/trisla/values-nasp.yaml`.
- GHCR pull secret if required by your environment (`ghcr-secret`).

### Resource Baseline (from existing docs)
- Minimum baseline referenced in `docs/INSTALLATION.md`: 4 CPU / 8 GB RAM / 50 GB disk.
- Production-oriented baseline in `docs/deployment/*`: 8 CPU / 16 GB RAM (or higher).

Use environment sizing compatible with your target profile before deploy.

## 4. Required Components

### 4.1 Infrastructure and Platform Dependencies
- Kubernetes (hard requirement for canonical flow).
- Helm (hard requirement for canonical flow).
- Kafka (required by current charted core flow).
- GHCR image access (required unless using public/available images with no auth restrictions).

### 4.2 Core TriSLA Components

| Service | Path | Port | Dependencies |
|---|---|---:|---|
| SEM-CSMF | `apps/sem-csmf` | 8080 | Kafka, OTLP endpoint |
| ML-NSMF | `apps/ml-nsmf` | 8081 | Kafka, OTLP endpoint |
| Decision Engine | `apps/decision-engine` | 8082 | ML-NSMF, SLA-Agent, OTLP |
| BC-NSSMF | `apps/bc-nssmf` | 8083 | Besu RPC, wallet secret, OTLP |
| SLA-Agent Layer | `apps/sla-agent-layer` | 8084 | NASP Adapter, BC-NSSMF, Kafka, OTLP |
| NASP Adapter | `apps/nasp-adapter` | 8085 | SEM-CSMF, Prometheus URL, K8s API |

### 4.3 Supporting Components in `helm/trisla`

| Service | Path | Port | Dependencies |
|---|---|---:|---|
| UI Dashboard | `apps/ui-dashboard` | 80 | Ingress/service exposure |
| Traffic Exporter | `apps/traffic-exporter` | 9105 | Prometheus scrape |
| Kafka | `apps/kafka` + chart deployment | 9092 | Event backbone consumers/producers |
| Besu | `apps/besu` + chart deployment | 8545/8546/30303 | BC-NSSMF integration |

Notes:
- `kafka` has a deployment template in `helm/trisla/templates/deployment-kafka.yaml`; there is no dedicated `service-kafka.yaml` in this chart.
- Portal backend/frontend are charted separately in `helm/trisla-portal` and are not part of the canonical flow in this document.

## 5. Deployment Methods

| Method | Use case | Scope | Limitation |
|---|---|---|---|
| Helm (principal) | Standard cluster installation | `helm/trisla` full core stack | Requires Kubernetes and validated values file |
| Docker Compose | Local experimentation | Local stack outside canonical K8s flow | Does not represent charted K8s runtime behavior |
| Ansible | Environment automation where playbooks exist | Orchestration around cluster operations | Playbook references appear in docs and must exist/align in your target repo |
| CI/CD | Automated release pipeline | Non-interactive deploy automation | Depends on pipeline files/secrets in your CI environment |

## 6. Canonical Installation Flow (Principal)

This is the single step-by-step flow for this repository:
1. Prepare environment.
2. Validate infrastructure.
3. Configure values.
4. Execute deploy.
5. Verify services.

## 7. Step-by-Step Installation

### 7.1 Prepare environment

```bash
kubectl cluster-info
kubectl get nodes
helm version
kubectl get namespace trisla || kubectl create namespace trisla
```

If GHCR credentials are required in your cluster:

```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<GITHUB_USER> \
  --docker-password=<GITHUB_PAT> \
  --docker-email=<EMAIL> \
  -n trisla
```

### 7.2 Validate infrastructure

Validate chart and rendering before install:

```bash
helm lint ./helm/trisla -f ./helm/trisla/values-nasp.yaml
helm template trisla ./helm/trisla -f ./helm/trisla/values-nasp.yaml --debug > /dev/null
```

Optional DNS pre-check (from current docs):

```bash
kubectl run -it --rm preflight-dns --image=busybox:1.36 --restart=Never -n trisla -- \
  nslookup kubernetes.default.svc.cluster.local
```

### 7.3 Configure `values.yaml`

Canonical values file for this flow: `helm/trisla/values-nasp.yaml`.

Minimum required checks before deploy:
- `global.imageRegistry`.
- `global.namespace`.
- `network.interface`, `network.nodeIP`, `network.gateway`.
- Production flags under `production.*`.
- Service images and digests/tags expected by your target release.

Important chart behavior:
- `templates/_helpers.tpl` enforces digest-based image resolution (`repo@digest`) and fails rendering if digest is absent for components using that helper.

### 7.4 Execute official deploy command

```bash
helm upgrade --install trisla ./helm/trisla \
  --namespace trisla \
  --create-namespace \
  --values ./helm/trisla/values-nasp.yaml \
  --wait \
  --timeout 15m
```

### 7.5 Bring up and verify services

```bash
helm status trisla -n trisla
kubectl get pods -n trisla
kubectl get svc -n trisla
kubectl get ingress -n trisla
```

Core health checks from running pods:

```bash
kubectl exec -n trisla deployment/trisla-sem-csmf -- curl -s http://localhost:8080/health
kubectl exec -n trisla deployment/trisla-ml-nsmf -- curl -s http://localhost:8081/health
kubectl exec -n trisla deployment/trisla-decision-engine -- curl -s http://localhost:8082/health
kubectl exec -n trisla deployment/trisla-bc-nssmf -- curl -s http://localhost:8083/health
kubectl exec -n trisla deployment/trisla-sla-agent-layer -- curl -s http://localhost:8084/health
kubectl exec -n trisla deployment/trisla-nasp-adapter -- curl -s http://localhost:8085/health
```

## 8. Expected System State

### Expected Deployments
- `trisla-sem-csmf`
- `trisla-ml-nsmf`
- `trisla-decision-engine`
- `trisla-bc-nssmf`
- `trisla-sla-agent-layer`
- `trisla-nasp-adapter`
- `trisla-ui-dashboard`
- `kafka`
- `trisla-besu`
- `trisla-traffic-exporter`

### Expected Services
- `trisla-sem-csmf`
- `trisla-ml-nsmf`
- `trisla-decision-engine`
- `trisla-bc-nssmf`
- `trisla-sla-agent-layer`
- `trisla-nasp-adapter`
- `trisla-ui-dashboard`
- `trisla-besu`
- `trisla-traffic-exporter`

### Expected Communication Links
- `decision-engine` reaches `ml-nsmf` and `sla-agent-layer`.
- `sla-agent-layer` reaches `nasp-adapter` and `bc-nssmf`.
- `bc-nssmf` reaches Besu RPC endpoint.
- `sem-csmf` and `ml-nsmf` publish/consume via Kafka settings.

## 9. Troubleshooting (Evidence-Based)

### Kafka not running / not reachable
Symptoms:
- SLA-Agent, SEM-CSMF, or ML-NSMF degraded behavior.
- Env vars point to `kafka:9092` or `kafka.trisla.svc.cluster.local:9092`, but broker is unavailable.

Checks:
```bash
kubectl get pods -n trisla | grep kafka
kubectl logs -n trisla -l app=kafka --tail=100
```

### Pods in `CrashLoopBackOff`
Checks:
```bash
kubectl get pods -n trisla
kubectl describe pod <pod-name> -n trisla
kubectl logs <pod-name> -n trisla --previous
```

Common evidence in this repo:
- Invalid/missing image pull settings.
- Missing external secrets (`bc-nssmf-wallet`, validator key secret).
- Invalid values in `values-nasp.yaml`.

### Invalid chart configuration
Checks:
```bash
helm lint ./helm/trisla -f ./helm/trisla/values-nasp.yaml
helm template trisla ./helm/trisla -f ./helm/trisla/values-nasp.yaml --debug
```

If render fails, fix the reported key in values (especially image digest expectations and required environment settings).

## 10. Final Checklist

- [ ] Infrastructure ready (`kubectl cluster-info`, nodes reachable, namespace created).
- [ ] `helm/trisla/values-nasp.yaml` reviewed and environment-specific values set.
- [ ] GHCR pull secret available (when required).
- [ ] Helm deploy command executed successfully.
- [ ] Core pods running and health endpoints responding.
- [ ] Service graph links validated (`decision-engine` <-> `ml-nsmf`/`sla-agent-layer`, `bc-nssmf` <-> `besu`, Kafka-dependent components operational).

## Appendix A — Script Audit

Requested scripts under `scripts/`:

| Script | Function | When to use | Dependencies |
|---|---|---|---|
| `scripts/deploy-trisla-nasp.sh` | Not found in this repository | N/A | N/A |
| `scripts/validate-nasp-infra.sh` | Not found in this repository | N/A | N/A |
| `scripts/auto-config-nasp.sh` | Not found in this repository | N/A | N/A |

Real deploy script found:

| Script | Function | When to use | Dependencies |
|---|---|---|---|
| `apps/besu/deploy/deploy-trisla-besu-nasp.sh` | Helm deploy workflow with prechecks for Besu-enabled stack | Besu + TriSLA blockchain-oriented rollout | Bash, kubectl, helm, Kubernetes cluster, `helm/trisla`, `values-nasp.yaml` |

## Appendix B — Image Validation (Helm + Mapping)

### Effective chart images from `helm/trisla/values.yaml`

| Service | Image |
|---|---|
| SEM-CSMF | `ghcr.io/abelisboa/trisla-sem-csmf@sha256:84b73a5b8df53fb4901041d96559878bd2248517277557496cb2b7b3effeb375` |
| ML-NSMF | `ghcr.io/abelisboa/trisla-ml-nsmf@sha256:b0922b2199830a766a6fd999213583973bc8209862f39a949de2d18010017187` |
| Decision Engine | `ghcr.io/abelisboa/trisla-decision-engine@sha256:5695c700be9b83bd11bdf846a5762f1f9ba3dde143c73f3cec2b55472bb4caa6` |
| BC-NSSMF | `ghcr.io/abelisboa/trisla-bc-nssmf@sha256:b0db5eef2128baddee2c1c3ea72fb5fec421afb1d87407e5f4a6aadd75f9f95a` |
| SLA-Agent | `ghcr.io/abelisboa/trisla-sla-agent-layer@sha256:824b641b7ff17ba52bd93d9c0aeb6f1a4a073575ff86719bd14f67f6a80becce` |
| NASP Adapter | `ghcr.io/abelisboa/trisla-nasp-adapter@sha256:34b5849eb81eb3b4cd3a858ff3dee3e8ab953b7ec8f66f4e83717b0cf8056529` |
| UI Dashboard | `ghcr.io/abelisboa/trisla-ui-dashboard@sha256:16e23f4de91582e56bfe4704c0139a3154c34c4a44780f17f3082b6195dbe6fb` |
| Traffic Exporter | `ghcr.io/abelisboa/trisla-traffic-exporter@sha256:a39455f913ea4f7355426b48613cc0479c7e549d099bdba520fd4fb563564f48` |
| Kafka | `ghcr.io/abelisboa/trisla-kafka@sha256:8291bed273105a3fc88df5f89096abf6a654dc92b0937245dcef85011f3fc5e6` |
| Besu | `ghcr.io/abelisboa/trisla-besu@sha256:ab84d26d678417b615c0833b4a34e9fe2778cec392a7e23596fa1607cf362efc` |

### Mapping reference file

`docs/deployment/HELM_IMAGE_MAPPING.md` exists and uses tag-based entries (for example `v3.9.4`) while the chart helper enforces digest-based resolution. During operations, treat chart-rendered image output as the execution source of truth.
