# TriSLA: A Preventive and Closed-Loop SLA-Aware Architecture for Explainable Multidomain Admission in 5G Networks

## Overview

TriSLA is a preventive and closed-loop SLA-aware architecture for explainable
multidomain admission in 5G networks. It evaluates whether a requested network
slice can be sustained before infrastructure resources are committed and then
uses runtime telemetry to supervise the admitted service.

TriSLA integrates semantic intent processing,
machine-learning feasibility inference, explainable admission decisions,
multidomain orchestration across RAN, Transport Network (TN), and 5G Core
(5GC), and closed-loop runtime assurance.

## Architecture

The current architecture is organized into three functional tiers:

| Tier | Responsibility |
| --- | --- |
| Intelligence Layer | Interprets SLA intent, creates canonical service profiles, evaluates predictive feasibility, and produces ACCEPT, RENEGOTIATE, or REJECT outcomes. |
| Execution Layer | Translates accepted decisions into coordinated provisioning through NASP across the RAN, TN, and 5GC domains. |
| Observability and Runtime Assurance Layer | Collects multidomain telemetry, detects performance drift, and supports closed-loop verification and remediation. |

The scientific interfaces are OBS-I1, RAN-I1, TN-I1, CN-I1, and SLAA-I1.
Control-plane services communicate through synchronous REST APIs using
structured JSON over HTTP and Kubernetes ClusterIP service discovery.

## Components

| Component | Scientific role |
| --- | --- |
| SLA Intake Gateway | Receives tenant SLA intent through POST /api/v1/sla/submit. |
| SEM-CSMF | Performs semantic request processing and generates canonical NEST profiles. |
| ML-NSMF | Provides model-agnostic feasibility, risk, confidence, and explainability outputs. |
| Decision Engine | Combines predictive indicators and policy constraints to decide ACCEPT, RENEGOTIATE, or REJECT. |
| NASP Adapter / NASP | Coordinates provisioning across the RAN, TN, and 5GC domains. |
| TELEMETRY | Aggregates multidomain observations for admission and runtime supervision. |
| SLA-Agent | Executes continuous Observe-Analyze-Decide supervision and closed-loop assurance. |

## Operational Workflow

    SLA request
    -> semantic processing and canonical NEST generation
    -> multidomain telemetry correlation
    -> ML feasibility inference and explainability
    -> Decision Engine: ACCEPT | RENEGOTIATE | REJECT
    -> NASP multidomain provisioning for accepted requests
    -> RAN / TN / 5GC activation and observability binding
    -> SLA-Agent runtime supervision and closed-loop assurance

Detailed implementation contracts and module-specific endpoints are documented
under [docs/](docs/). Internal identifiers such as I-01 through I-06 describe
preserved implementation contracts; they are not the scientific interface
nomenclature listed above.

## Experimental Environment

The evaluated cloud-native prototype uses a multi-node Kubernetes cluster with
containerd, Helm, and ConfigMaps. Its multidomain testbed includes UERANSIM for
the gNB and UE, ONOS and Mininet with OpenFlow for transport, and free5GC for
the core. Prometheus, Grafana, OpenTelemetry, and Jaeger provide telemetry and
observability support.

## Experimental Evaluation

The article reports the following central results under the evaluated
experimental conditions:

- semantic processing: 25.37 +/- 3.38 ms; classification accuracy and macro F1
  are 100%, while canonical mapping and attribute consistency vary by scenario;
- default Random Forest classifier: 98.68 +/- 0.48% accuracy; XGBoost reaches
  99.51 +/- 0.33% in the comparative benchmark;
- explainable inference pipeline: 4.07 ms for normalization, 109.00 ms for
  model execution, and 118.59 ms of asynchronous SHAP overhead, totaling
  231.66 ms;
- preventive admission over 240 requests: 123 ACCEPT, 5 RENEGOTIATE, and 112
  REJECT, yielding a 53.3% effective admission rate and 100.0% SLA satisfaction
  among admitted requests;
- closed-loop assurance: all 12 evaluated anomalies recovered across 24
  executions, with a 4224 +/- 9 ms closed-loop cycle;
- end-to-end workflow: 4046.3 +/- 736.5 ms, dominated by NSI instantiation.

These results are scoped to the reported experiments and do not imply universal
SLA satisfaction or production-readiness.

## Dataset

All reported evaluations use a single consolidated experimental dataset with
objective-specific subsets for the different evaluation tasks. The canonical
Parquet dataset and its CSV publication export are available in
[datasets/](datasets/), together with schema, integrity, and reproducibility
information.

## Limitations and Future Work

The reported limitations include SHAP computation overhead, degradation of
canonical semantic mapping under extreme linguistic stress, and offline model
training that may be affected by concept drift. Future work includes larger
deployments, higher request rates, more heterogeneous topologies, adaptive
policies, online retraining, and reinforcement-learning strategies.

## Quick Start

    kubectl cluster-info
    kubectl get nodes
    helm version
    helm upgrade --install trisla ./helm/trisla --namespace trisla --create-namespace --values ./helm/trisla/values-nasp.yaml --wait --timeout 15m

Deployment details and validation procedures are in
[docs/README.md](docs/README.md).

## Repository Structure

| Path | Purpose |
| --- | --- |
| [apps/](apps/) | Public service implementations and preserved implementation extensions. |
| [docs/](docs/) | Scientific overview, implementation references, and explicitly classified historical material. |
| [helm/](helm/) | Kubernetes deployment charts and experimental deployment configuration. |
| [datasets/](datasets/) | Canonical experimental dataset, publication export, and integrity documentation. |

## Historical and Implementation Extensions

The repository preserves additional implementation and historical artifacts,
including BC-NSSMF, Hyperledger Besu and smart-contract governance, Kafka and
gRPC integration code, internal I-01 through I-06 runtime contracts, and an
earlier UI dashboard. These artifacts remain available for implementation
traceability and further experimentation, but they are not components of the
architecture described in the current article.

Relevant references include:

- [Current implementation interfaces](docs/modules/interfaces.md)
- [BC-NSSMF historical implementation extension](docs/modules/bc-nssmf.md)
- [Module documentation](docs/modules/)
- [License: Apache-2.0](LICENSE)

## Documentation

Reference article:

> TriSLA: A Preventive and Closed-Loop SLA-Aware Architecture for Explainable Multidomain Admission in 5G Networks
