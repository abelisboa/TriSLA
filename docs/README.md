# TriSLA

TriSLA is a tri-dimensional SLA-aware orchestration architecture for 5G/O-RAN network slicing. It evaluates SLA feasibility at request time, before resource commitment, by combining semantic intent processing, runtime multidomain telemetry, machine-learning risk prediction, deterministic admission rules, detached NASP orchestration, blockchain evidence, and runtime assurance.

The public repository contains the implementation and canonical module documentation for the frozen public baseline. It presents the TriSLA project, architecture, installation path, validation checks, and module references for public use.

## Research Scope

TriSLA addresses preventive SLA admission for network slices in environments where RAN, transport, and core conditions affect whether a requested SLA can be sustained.

The research question captured by the frozen article is:

```text
Can SLA feasibility be assessed at request time using runtime multidomain telemetry while preserving explicit causal boundaries between admission, orchestration, reconciliation, lifecycle, and governance?
```

The frozen evidence supports preventive admission with explicit boundaries. TriSLA does not claim balanced multidomain causal dominance, orchestration-to-admission feedback, core-driven admission, continuous autonomous reevaluation, or standards certification.

## Architecture

TriSLA separates responsibilities across intelligence, execution, governance, telemetry, observability, and presentation layers.

### Official Modules

| Module | Responsibility |
| --- | --- |
| Portal Frontend | User-facing web interface. It renders SLA submission, admission, governance, runtime, and monitoring views by consuming Portal Backend APIs. It does not decide SLA, generate telemetry, produce governance, or produce runtime assurance. |
| Portal Backend | Frontend-facing API layer. It receives SLA submissions, collects submission-time telemetry, relays admission requests to SEM-CSMF, triggers orchestration after ACCEPT, propagates governance metadata, and delegates runtime reassessment to SLA-Agent. |
| SEM-CSMF | Semantic front layer. It interprets natural-language or structured SLA intents, validates them against the ontology, materializes GST/NEST artifacts, persists intent/NEST state, and forwards structured input to the Decision Engine through the production HTTP path. |
| Decision Engine | SLA admission authority. It evaluates SLA viability, calls ML-NSMF for prediction, applies PRB gates, slice-aware thresholds, multidomain scoring, and returns ACCEPT, RENEGOTIATE, or REJECT with explainability and decision evidence. |
| ML-NSMF | Predictive intelligence layer. It serves synchronous inference for the Decision Engine, using the active model bundle to return risk, viability, confidence, slice-adjusted risk, and explainability metadata. It does not make the final admission decision. |
| NASP Adapter | Post-admission orchestration and infrastructure integration layer. It provisions Network Slice Instances on Kubernetes, manages capacity reservations, exposes multidomain metrics, and integrates with Free5GC, UERANSIM, ONOS, Prometheus, and SEM-CSMF where configured. |
| BC-NSSMF | On-chain evidence authority. It registers accepted SLA evidence through SLAContract.sol on Hyperledger Besu and returns transaction hash, block number, and blockchain status. It does not decide admission or compose governance metadata. |
| SLA-Agent Layer | Temporal reassessment and runtime assurance authority. It performs telemetry reassessment, compliance evaluation, explainability generation, and runtime assurance through active HTTP endpoints. |

## Frozen Runtime Flow

The canonical interface chain is:

```text
Portal Frontend
-> Portal Backend
-> SEM-CSMF
-> Decision Engine
-> ML-NSMF
-> Decision Engine
-> Portal Backend
-> NASP Adapter
-> BC-NSSMF
-> SLA-Agent
-> Portal Frontend
```

Operationally:

1. Portal Frontend submits a natural-language or structured SLA request to Portal Backend.
2. Portal Backend normalizes the request and collects a Prometheus-backed telemetry snapshot.
3. SEM-CSMF interprets and persists semantic SLA intent/NEST state.
4. Decision Engine evaluates admission through POST /evaluate.
5. Decision Engine calls ML-NSMF through POST /api/v1/predict.
6. Decision Engine returns AC, RENEG, or REJ with evidence.
7. For accepted SLAs, Portal Backend triggers NASP Adapter orchestration.
8. After successful orchestration, Portal Backend calls BC-NSSMF for on-chain evidence.
9. Governance metadata is propagated back through SEM-CSMF and rendered by Portal Frontend.
10. SLA-Agent provides runtime reassessment and assurance through delegated HTTP paths.

Orchestration and reconciliation do not recompute admission. OTEL traces are observability signals, not the source of the telemetry snapshot.

## Infrastructure Requirements

The canonical deployment target is Kubernetes with Helm.

Required or charted components:

| Component | Role |
| --- | --- |
| Kubernetes | Runtime substrate for TriSLA services, CRDs, services, pods, and reconciliation. |
| Docker / OCI images | Container build and execution format; published images are expected under GHCR paths. |
| Helm | Deployment mechanism for helm/trisla, helm/trisla-portal, and Besu chart assets. |
| Prometheus | Primary telemetry and observability metrics source. |
| Grafana | Dashboard and runtime monitoring visualization. |
| OpenTelemetry | Service tracing and instrumentation. Not the telemetry snapshot source. |
| Jaeger / Tempo | Trace inspection and tracing backend paths for OTEL data. |
| Hyperledger Besu | Permissioned blockchain runtime for BC-NSSMF evidence. |
| Free5GC | 5G core integration target used by NASP-related runtime paths. |
| UERANSIM | RAN/UE emulation and binding context. |
| ONOS | Conditional transport binding and observation context. |
| Kafka | Charted event backbone for components that retain Kafka integration, although REST is the admission hot path. |

## Installation

### Prerequisites

```bash
kubectl cluster-info
kubectl get nodes
helm version
```

Prepare the namespace:

```bash
kubectl get namespace trisla || kubectl create namespace trisla
```

If your cluster requires authenticated GHCR pulls:

```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<GITHUB_USER> \
  --docker-password=<GITHUB_PAT> \
  --docker-email=<EMAIL> \
  -n trisla
```

### Infrastructure Preparation

Validate chart rendering before installation:

```bash
helm lint ./helm/trisla -f ./helm/trisla/values-nasp.yaml
helm template trisla ./helm/trisla -f ./helm/trisla/values-nasp.yaml --debug > /dev/null
```

Optional DNS pre-check:

```bash
kubectl run -it --rm preflight-dns --image=busybox:1.36 --restart=Never -n trisla -- \
  nslookup kubernetes.default.svc.cluster.local
```

### Repository Clone

```bash
git clone https://github.com/abelisboa/TriSLA.git
cd TriSLA
```

### Container Images

The Helm charts reference GHCR images for SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent Layer, NASP Adapter, Portal Backend, and Portal Frontend. Review helm/trisla/values-nasp.yaml and helm/trisla-portal/values.yaml for image tags, digests, namespace, and environment-specific values before deployment.

### Helm Deployment

Deploy the core stack:

```bash
helm upgrade --install trisla ./helm/trisla \
  --namespace trisla \
  --create-namespace \
  --values ./helm/trisla/values-nasp.yaml \
  --wait \
  --timeout 15m
```

Deploy the portal chart:

```bash
helm upgrade --install trisla-portal ./helm/trisla-portal \
  --namespace trisla \
  --values ./helm/trisla-portal/values.yaml \
  --wait \
  --timeout 15m
```

### Service Validation

```bash
helm status trisla -n trisla
helm status trisla-portal -n trisla
kubectl get pods -n trisla
kubectl get svc -n trisla
kubectl get ingress -n trisla
```

### Health Checks

```bash
kubectl exec -n trisla deploy/trisla-sem-csmf -- curl -s http://localhost:8080/health
kubectl exec -n trisla deploy/trisla-ml-nsmf -- curl -s http://localhost:8081/health
kubectl exec -n trisla deploy/trisla-decision-engine -- curl -s http://localhost:8082/health
kubectl exec -n trisla deploy/trisla-bc-nssmf -- curl -s http://localhost:8083/health
kubectl exec -n trisla deploy/trisla-sla-agent-layer -- curl -s http://localhost:8084/health
kubectl exec -n trisla deploy/trisla-nasp-adapter -- curl -s http://localhost:8085/health
```

Portal services are exposed by the portal chart values:

```text
frontend NodePort: 32001
backend NodePort: 32002
```

### Telemetry Validation

```bash
kubectl get pods -n monitoring
kubectl get servicemonitor -A
kubectl exec -n trisla deploy/trisla-sem-csmf -- curl -s http://localhost:8080/metrics
kubectl exec -n trisla deploy/trisla-decision-engine -- curl -s http://localhost:8082/metrics
kubectl exec -n trisla deploy/trisla-nasp-adapter -- curl -s http://localhost:8085/metrics
```

The primary runtime telemetry object is:

```text
telemetry_snapshot = { ran, transport, core }
```

Prometheus-backed collectors are the primary source for this object.

### Blockchain Validation

```bash
kubectl get pods -n trisla | grep besu
kubectl exec -n trisla deploy/trisla-bc-nssmf -- curl -s http://localhost:8083/health
kubectl exec -n trisla deploy/trisla-bc-nssmf -- curl -s http://localhost:8083/health/ready
```

Expected blockchain evidence on successful accepted and committed paths:

```text
tx_hash
block_number
bc_status=COMMITTED
```

### Admission Validation

The active admission entrypoint is the Portal Backend:

```text
POST /api/v1/sla/submit
```

Expected outcomes:

```text
AC     = ACCEPT
RENEG  = RENEGOTIATE
REJ    = REJECT
```

An ACCEPT path can trigger NASP orchestration and blockchain registration. REJECT and RENEGOTIATE remain admission results and do not represent successful orchestration.

## Expected Runtime State

Expected core deployments:

```text
trisla-sem-csmf
trisla-ml-nsmf
trisla-decision-engine
trisla-bc-nssmf
trisla-sla-agent-layer
trisla-nasp-adapter
trisla-ui-dashboard
kafka
trisla-besu
trisla-traffic-exporter
trisla-portal-backend
trisla-portal-frontend
```

Expected service checks:

```text
SEM-CSMF /health = healthy
ML-NSMF /health = healthy
Decision Engine /health = healthy
BC-NSSMF /health and /health/ready = healthy or explicitly degraded
SLA-Agent /health = healthy
NASP Adapter /health = healthy
Portal Backend health endpoints = reachable
Portal Frontend = reachable through configured service exposure
```

Expected evidence categories:

| Category | Expected evidence |
| --- | --- |
| Admission ACCEPT | Decision Engine result AC, decision evidence, optional orchestration trigger. |
| Admission REJECT | Decision Engine result REJ, decision evidence, no successful orchestration. |
| Runtime Assurance | SLA-Agent runtime assurance, domain compliance, metric explainability, violations, warnings, drift, and bottleneck fields where available. |
| Governance Evidence | BC-NSSMF transaction hash, block number, blockchain status; Portal-derived governance registration fields. |
| Blockchain Evidence | Hyperledger Besu transaction receipt surfaced through BC-NSSMF. |

## Repository Structure

```text
apps/
docs/
helm/
```

| Path | Purpose |
| --- | --- |
| apps/ | Service implementation for TriSLA modules, portal components, exporters, Kafka/Besu support, and runtime services. |
| docs/ | Public canonical module documentation and operational references for the frozen public baseline. |
| helm/ | Kubernetes deployment charts for the TriSLA core stack, portal stack, and Besu assets. |

Canonical module references:

```text
docs/modules/sem-csmf.md
docs/modules/nasp-adapter.md
docs/modules/decision-engine.md
docs/modules/ml-nsmf.md
docs/modules/bc-nssmf.md
docs/modules/sla-agent-layer.md
docs/modules/telemetry.md
docs/modules/observability.md
docs/modules/portal-backend.md
docs/modules/portal-frontend.md
docs/modules/interfaces.md
```

## References

TriSLA is aligned with the dissertation and frozen scientific article, and uses standards and platforms as conceptual or implementation references where evidenced:

- TriSLA Dissertation, especially the frozen prototype, results, implications, and limitations chapters.
- TriSLA scientific publication, "TriSLA: A Tri-Dimensional SLA-Aware Orchestration Architecture for O-RAN Networks with Explainable AI and Blockchain Compliance".
- 3GPP network slicing and management references, including TS 28.541 where applicable.
- GSMA NG.116 for GST/canonical SLA alignment.
- O-RAN Alliance architecture references for open RAN architectural context.
- ETSI ZSM for zero-touch service management concepts.
- Hyperledger Besu for permissioned blockchain execution.
- NASP as the Network Slice as a Service Platform integration context.


## Public Deployment Configuration

The public release contains no private wallet or workstation-specific network defaults. Supply the BC-NSMF wallet through a Kubernetes Secret and configure `bcNssmf.wallet.existingSecret` and `bcNssmf.wallet.key`. Set `network.interface`, `network.nodeIP`, and `network.gateway` for the target environment. The RAN/UE/UPF telemetry proxy is disabled by default; enable `ranUeUpfProxy.enabled` only after providing an immutable public image digest and deployment-specific endpoints.
