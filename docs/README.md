# TriSLA Documentation

This documentation distinguishes the current scientific architecture from
implementation-specific runtime details and preserved historical extensions.
Those levels provide complementary evidence but must not be interpreted as a
single architectural baseline.

## Current Scientific Architecture

TriSLA is a preventive and closed-loop SLA-aware architecture for explainable
multidomain admission in 5G networks. It evaluates feasibility before resource
commitment and uses runtime telemetry for continuous assurance across RAN, TN,
and 5GC.

### Functional tiers

1. **Intelligence Layer** - SLA Intake Gateway, SEM-CSMF, ML-NSMF, and Decision
   Engine.
2. **Execution Layer** - NASP Adapter / NASP and the RAN, TN, and 5GC domain
   controllers.
3. **Observability and Runtime Assurance Layer** - TELEMETRY and SLA-Agent.

### Scientific workflow

    Tenant SLA intent
    -> SLA Intake Gateway
    -> SEM-CSMF semantic processing and canonical NEST
    -> multidomain telemetry correlation
    -> ML-NSMF feasibility inference and explainability
    -> Decision Engine: ACCEPT | RENEGOTIATE | REJECT
    -> NASP provisioning across RAN / TN / 5GC
    -> observability binding
    -> SLA-Agent closed-loop runtime assurance

The scientific interface names are:

| Interface | Scientific boundary |
| --- | --- |
| OBS-I1 | Multidomain telemetry and observability input. |
| RAN-I1 | Southbound RAN provisioning and observation. |
| TN-I1 | Southbound transport provisioning and observation. |
| CN-I1 | Southbound 5GC provisioning and observation. |
| SLAA-I1 | Runtime supervision initialization and assurance exchange. |

Control-plane inter-service communication uses synchronous REST APIs,
structured JSON over HTTP, and Kubernetes ClusterIP service discovery.

### Prototype

The evaluated prototype runs on a multi-node Kubernetes cluster using
containerd, Helm, and ConfigMaps. The testbed uses the namespaces trisla,
ns-core, ueransim, nasp-transport, and monitoring.

| Domain or function | Evaluated technology |
| --- | --- |
| RAN | UERANSIM gNB and UE |
| Transport | ONOS, Mininet, and OpenFlow |
| 5GC | free5GC with NRF, NSSF, PCF, AMF, SMF, UPF, and MongoDB |
| Observability | Prometheus, Grafana, OpenTelemetry, and Jaeger |

### Scientific ML baseline

The evaluated default model is a scikit-learn Random Forest classifier with
320 trees, 19 features, and an approximate size of 0.36 MB. The comparative
benchmark reports:

| Model | Accuracy |
| --- | ---: |
| Random Forest | 98.68 +/- 0.48% |
| XGBoost | 99.51 +/- 0.33% |
| LightGBM | 99.17 +/- 0.56% |
| LSTM | 92.78 +/- 1.35% |
| MLP | 71.81 +/- 2.00% |

The 99.51% result belongs to XGBoost, not to the default Random Forest.
Detailed SHAP attribution is processed asynchronously in the scientific
prototype. The article reports 4.07 ms for input normalization, 109.00 ms for
model execution, 118.59 ms of explainability overhead, and 231.66 ms for the
cumulative predictive pipeline.

### Evaluation summary

- Semantic processing totals 25.37 +/- 3.38 ms. Classification accuracy and
  macro F1 are 100%; canonical mapping and attribute consistency vary across
  C0-C7.
- Preventive admission over 240 requests produces 123 ACCEPT, 5 RENEGOTIATE,
  and 112 REJECT outcomes, for a 53.3% effective admission rate. SLA
  satisfaction is 100.0% among admitted requests, compared with 51.2% for
  Always Accept and 79.2% for Static Threshold.
- Across 24 runtime executions, Closed-Loop mode reports 2090 +/- 3 ms
  detection, 52 +/- 7 ms correction, 2082 +/- 3 ms recovery/revalidation, and
  4224 +/- 9 ms total. All 12 evaluated anomalies were recovered.
- Mean E2E latency is 4046.3 +/- 736.5 ms: M01 SLA Intake and Semantic
  Processing 110.7 +/- 10.4 ms, M02 Feasibility and Decision
  936.3 +/- 64.6 ms, M03 NSI Instantiation 2.74 s +/- 720.3 ms,
  M04 Lifecycle Tracking / Observability Binding 137.2 +/- 102.7 ms, and
  M05 Response Finalization 0.16 +/- 0.02 ms.

Results are limited to the evaluated conditions. The article identifies SHAP
overhead, semantic canonical-mapping degradation under extreme linguistic
stress, and offline training subject to concept drift as limitations.

## Experimental Dataset

All reported evaluations use one consolidated experimental dataset with
objective-specific subsets. See [datasets/README.md](../datasets/README.md)
for the canonical Parquet artifact, CSV publication export, schema, and hashes.

## Implementation Documentation

The public repository includes concrete runtime behavior beyond the scientific
abstraction. These references describe deployed APIs and implementation
boundaries without redefining the current scientific architecture:

- [SEM-CSMF](modules/sem-csmf.md)
- [Decision Engine](modules/decision-engine.md)
- [ML-NSMF](modules/ml-nsmf.md)
- [NASP Adapter](modules/nasp-adapter.md)
- [SLA-Agent Layer](modules/sla-agent-layer.md)
- [Telemetry](modules/telemetry.md)
- [Observability](modules/observability.md)
- [Portal Backend](modules/portal-backend.md)
- [Portal Frontend](modules/portal-frontend.md)
- [Implementation interface contracts](modules/interfaces.md)

The active admission path is REST-first. Kafka and gRPC artifacts are preserved
where implemented, but they are not the primary scientific communication model.

### Deployment

    helm upgrade --install trisla ./helm/trisla --namespace trisla --create-namespace --values ./helm/trisla/values-nasp.yaml --wait --timeout 15m

Validate the deployment with kubectl get pods -n trisla, service-specific
/health endpoints, and Prometheus /metrics endpoints. Environment-specific
network values and credentials must be supplied by the operator.

## Historical / Experimental Extensions

The repository preserves BC-NSSMF, Hyperledger Besu, smart contracts,
blockchain-governance views, Kafka and gRPC code paths, I-01 through I-06
runtime identifiers, and an earlier UI dashboard. They provide implementation
and historical traceability but are not components of the current scientific
architecture in the updated article.

Documentation is retained at:

- [BC-NSSMF historical implementation extension](modules/bc-nssmf.md)
- [Specialized BC-NSSMF documentation](bc-nssmf/README.md)
- [Portal implementation](portal/README.md)
- [Helm deployment configuration](../helm/trisla/README.md)

## Scientific Reference

Current article:

> TriSLA: A Preventive and Closed-Loop SLA-Aware Architecture for Explainable Multidomain Admission in 5G Networks
