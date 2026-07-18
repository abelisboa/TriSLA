# TriSLA

TriSLA is a tri-dimensional SLA-aware architecture for 5G/O-RAN network slicing. Its central research problem is how to decide, at the moment an SLA is requested, whether sufficient resources exist across the network-slice lifecycle to support admission while considering RAN, transport, and core domains.

The project focuses on preventive SLA assurance: before a slice is accepted, TriSLA combines semantic interpretation, artificial intelligence, blockchain-based governance, and multidomain observability to evaluate feasibility and produce an auditable admission decision. The architecture is conceptually aligned with 3GPP, GSMA, O-RAN, and ETSI ZSM references without declaring formal certification or standards compliance.

TriSLA is organized around three official scientific pillars. SEM-CSMF interprets SLA intents, validates them against the ontology, and materializes GST/NEST artifacts. ML-NSMF evaluates viability, predicts risk, and produces explainability metadata for the admission process. BC-NSSMF registers accepted SLA evidence through smart contracts, supporting traceability, governance, and immutable evidence.

Complementary runtime components complete the control path: the Decision Engine acts as the SLA admission authority, while the SLA-Agent Layer provides temporal reassessment and runtime assurance. Together, these components support a reproducible public implementation of preventive, explainable, and governable SLA management for network slicing.

This root README is the GitHub landing page for the project. The complete public documentation entry point remains [docs/README.md](docs/README.md).

## Architecture

| Module | Official responsibility |
| --- | --- |
| SEM-CSMF | Semantic front layer. It interprets SLA intents, validates them against the ontology, materializes GST/NEST artifacts, persists intent/NEST state, and forwards structured input to the Decision Engine through the production HTTP path. |
| Decision Engine | SLA admission authority. It receives structured input from SEM-CSMF, calls ML-NSMF for risk prediction, applies policy-governed admission rules, and returns AC, RENEG, or REJ with decision evidence. |
| ML-NSMF | Predictive intelligence layer. It receives feature payloads from the Decision Engine, runs trained model inference, and returns risk scores and explainability metadata. It does not make final SLA decisions. |
| NASP Adapter | Post-admission orchestration and infrastructure integration layer. It provisions Network Slice Instances on Kubernetes, manages capacity reservations, exposes multidomain metrics, and integrates with NASP-related infrastructure. |
| BC-NSSMF | On-chain evidence authority. It registers accepted SLA evidence through SLAContract.sol on Hyperledger Besu and returns transaction hash, block number, and blockchain status. |
| SLA-Agent Layer | Temporal reassessment and runtime assurance authority. It performs telemetry reassessment, compliance evaluation, explainability generation, and runtime assurance through active HTTP endpoints. |
| Portal Backend | Frontend-facing API layer. It receives SLA submissions, collects submission-time telemetry, relays admission requests to SEM-CSMF, triggers orchestration after ACCEPT, propagates governance metadata, and delegates runtime reassessment to SLA-Agent. |
| Portal Frontend | User-facing web interface. It renders SLA submission, admission, governance, runtime, and monitoring views by consuming Portal Backend APIs. |

## Frozen E2E Flow

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

The production admission path uses REST interfaces documented in [docs/modules/interfaces.md](docs/modules/interfaces.md). Orchestration and reconciliation do not recompute admission. Governance evidence is produced by BC-NSSMF, normalized by Portal Backend, persisted through SEM-CSMF, and rendered by Portal Frontend.

## Infrastructure

The public baseline documents these infrastructure and observability components where evidenced:

| Component | Role |
| --- | --- |
| Kubernetes | Runtime substrate for services, CRDs, pods, services, and reconciliation. |
| Helm | Deployment mechanism for the TriSLA core, portal, and Besu charts. |
| Docker / OCI images | Container format for the published services. |
| Prometheus | Primary telemetry and observability metrics source. |
| Grafana | Runtime monitoring and dashboard visualization. |
| OpenTelemetry | Service tracing and instrumentation; not the telemetry snapshot source. |
| Jaeger / Tempo | Trace inspection and tracing backend paths for OTEL data. |
| Hyperledger Besu | Permissioned blockchain runtime for BC-NSSMF evidence. |
| Free5GC | 5G core integration target used by NASP-related runtime paths. |
| UERANSIM | RAN/UE emulation and binding context. |
| ONOS | Conditional transport binding and observation context. |

## Quick Start

Prerequisites:

```bash
kubectl cluster-info
kubectl get nodes
helm version
```

Deploy the core stack:

```bash
helm upgrade --install trisla ./helm/trisla \
  --namespace trisla \
  --create-namespace \
  --values ./helm/trisla/values-nasp.yaml \
  --wait \
  --timeout 15m
```

Deploy the portal stack:

```bash
helm upgrade --install trisla-portal ./helm/trisla-portal \
  --namespace trisla \
  --values ./helm/trisla-portal/values.yaml \
  --wait \
  --timeout 15m
```

Validate services:

```bash
helm status trisla -n trisla
helm status trisla-portal -n trisla
kubectl get pods -n trisla
kubectl get svc -n trisla
```

Health checks:

```bash
kubectl exec -n trisla deploy/trisla-sem-csmf -- curl -s http://localhost:8080/health
kubectl exec -n trisla deploy/trisla-ml-nsmf -- curl -s http://localhost:8081/health
kubectl exec -n trisla deploy/trisla-decision-engine -- curl -s http://localhost:8082/health
kubectl exec -n trisla deploy/trisla-bc-nssmf -- curl -s http://localhost:8083/health
kubectl exec -n trisla deploy/trisla-sla-agent-layer -- curl -s http://localhost:8084/health
kubectl exec -n trisla deploy/trisla-nasp-adapter -- curl -s http://localhost:8085/health
```

Detailed installation, telemetry, blockchain, and admission validation steps are in [docs/README.md](docs/README.md).

## Repository Structure

```text
apps/
docs/
helm/
```

| Path | Purpose |
| --- | --- |
| [apps/](apps/) | Service implementations for TriSLA modules, portal components, exporters, Kafka/Besu support, and runtime services. |
| [docs/](docs/) | Public canonical module documentation and operational references for the frozen public baseline. |
| [helm/](helm/) | Kubernetes deployment charts for the TriSLA core stack, portal stack, and Besu assets. |

## Documentation

- [Project documentation](docs/README.md)
- [Canonical module documentation](docs/modules/)
- [Runtime interface chain](docs/modules/interfaces.md)
- [License: Apache-2.0](LICENSE)
- [SEM-CSMF](docs/modules/sem-csmf.md)
- [Decision Engine](docs/modules/decision-engine.md)
- [ML-NSMF](docs/modules/ml-nsmf.md)
- [NASP Adapter](docs/modules/nasp-adapter.md)
- [BC-NSSMF](docs/modules/bc-nssmf.md)
- [SLA-Agent Layer](docs/modules/sla-agent-layer.md)

## References

TriSLA is aligned with the dissertation and frozen scientific article, and uses standards and platforms as conceptual or implementation references where evidenced:

- 3GPP network slicing and management references, including TS 28.541 where applicable.
- GSMA NG.116 for GST/canonical SLA alignment.
- O-RAN Alliance architecture references for open RAN architectural context.
- ETSI ZSM for zero-touch service management concepts.
- Hyperledger Besu for permissioned blockchain execution.
- NASP as the Network Slice as a Service Platform integration context.

