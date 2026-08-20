# TriSLA: A Preventive and Closed-Loop SLA-Aware Architecture for Explainable Multidomain Admission in 5G Networks

**Authors:** Abel J. R. Lisboa, Gustavo Z. Bruno, and Cristiano B. Both

## Abstract

TriSLA is a preventive and closed-loop SLA-aware architecture for multidomain
5G network slicing. It addresses the limits of reactive SLA management by
evaluating whether a requested slice is feasible before infrastructure
resources are committed, then supervising the admitted service with runtime
telemetry.

The architecture combines natural-language semantic interpretation,
ontology-assisted service profiling, machine-learning-based feasibility
inference, explainable admission decisions, multidomain provisioning, and
closed-loop runtime assurance across Radio Access Network (RAN), Transport
Network (TN), and 5G Core (5GC) domains. The research prototype extends the
Network Slice as a Service Platform (NASP) and runs its control services as
containerized microservices in a multi-node Kubernetes environment.

## Architecture

TriSLA is organized into three scientific functional tiers:

| Tier | Components | Responsibility |
| --- | --- | --- |
| Intelligence Layer | SLA Intake Gateway, SEM-CSMF, ML-NSMF, Decision Engine | Normalize tenant intent into a canonical NEST profile, correlate the request with multidomain telemetry, estimate feasibility and risk, and return `ACCEPT`, `RENEGOTIATE`, or `REJECT`. |
| Execution Layer | NASP Adapter and RAN, TN, and 5GC domain controllers | Translate accepted decisions into coordinated domain provisioning and confirm end-to-end service readiness. |
| Observability and Runtime Assurance Layer | Multidomain telemetry aggregation and SLA-Agent | Collect operational metrics, bind runtime context to the admitted service, detect performance drift, and drive closed-loop remediation. |

The end-to-end scientific workflow is:

```text
Tenant SLA intent
  -> SLA Intake Gateway
  -> SEM-CSMF semantic normalization and canonical NEST profile
  -> multidomain telemetry snapshot
  -> ML-NSMF feasibility, risk, confidence, and explainability
  -> Decision Engine: ACCEPT | RENEGOTIATE | REJECT
  -> NASP Adapter and domain provisioning after ACCEPT
  -> observability context binding
  -> SLA-Agent continuous runtime supervision
  -> telemetry feedback and closed-loop remediation
```

Admission and orchestration cover semantic intake, predictive decision,
multidomain provisioning, observability binding, and response finalization.
After activation, the SLA-Agent executes an Observe–Analyze–Decide cycle using
live RAN, TN, and 5GC telemetry.

## TriSLA Prototype

The article prototype maps the architecture to containerized microservices in
a multi-node Kubernetes cluster. Helm packages the control plane, ConfigMaps
supply runtime configuration, and ClusterIP services support inter-service
REST communication.

| Area | Article prototype |
| --- | --- |
| Control plane | SLA Intake Gateway, SEM-CSMF, ML-NSMF, Decision Engine, NASP Adapter, and SLA-Agent in the `trisla` namespace |
| RAN | UERANSIM v4.2.1 with containerized gNB and UE workloads |
| Transport | ONOS, Mininet, and programmable OpenFlow paths |
| 5G Core | free5GC v3.1.1 with AMF, SMF, UPF, NRF, PCF, NSSF, and MongoDB |
| Observability | Prometheus, Grafana, OpenTelemetry, and Jaeger |
| Workload generation | UE connection bursts, `iperf3` cross-traffic, link impairment, and Linux compute stress |

## Experimental Environment

The article evaluates TriSLA in five Kubernetes namespaces: `trisla` for the
control plane, `ueransim` for RAN emulation, `nasp-transport` for the transport
domain, `ns-core` for free5GC, and `monitoring` for observability services.
Prometheus collects PRB utilization, transport latency, jitter, packet loss,
throughput, and 5GC CPU and memory measurements before admission requests.

Eight controlled scenarios cover nominal and stressed multidomain conditions:

| Scenarios | Conditions | Evaluation use |
| --- | --- | --- |
| C0 | All domains nominal | Semantic, ML, admission, and runtime reference condition |
| C1–C3 | One stressed domain: RAN, TN, or 5GC | Single-domain behavior and closed-loop remediation |
| C4–C6 | Two concurrently stressed domains | Compound multidomain feasibility and semantic robustness |
| C7 | RAN, TN, and 5GC stressed | Full multidomain stress |

The evaluated service categories are URLLC, eMBB, and mMTC. Semantic and ML
evaluations use observations from C0–C7; runtime assurance focuses on C0–C3
to isolate recovery and revalidation behavior.

## Experimental Evaluation

The article reports the following principal results under its controlled
multidomain testbed conditions:

| Evaluation | Reported result |
| --- | --- |
| Semantic processing | `25.37 ± 3.38 ms` total latency |
| Default feasibility classifier | Random Forest accuracy of `98.68 ± 0.48%` |
| Best compared classifier | XGBoost accuracy of `99.51 ± 0.33%` |
| Explainable feasibility pipeline | `231.66 ms` total: `4.07 ms` input normalization, `109.00 ms` model execution, and `118.59 ms` explainability overhead; SHAP attribution runs asynchronously |
| Preventive admission | Across 240 requests: 123 accepted, 5 renegotiated, and 112 rejected; effective admission rate `53.3%` |
| SLA satisfaction among admitted slices | TriSLA `100.0%`; always-accept baseline `51.2%`; static-threshold baseline `79.2%` |
| Runtime assurance | 24 executions across C0–C3; all 12 detected anomalies in Closed-Loop mode recovered; total cycle `4224 ± 9 ms` |
| End-to-end admission workflow | `4046.3 ± 736.5 ms`, dominated by network slice instantiation |

These values characterize the evaluated prototype and conditions; they are not
general performance guarantees for every deployment.

## Installation

### Requirements

#### Deployment prerequisites

- A Kubernetes cluster and a configured `kubectl` context. The repository does
  not currently specify a minimum supported Kubernetes version.
- Helm 3. The charts use Helm chart API v2; a minimum Helm 3 release is not
  specified.
- Access from the cluster to the configured container registry. Default images
  use `ghcr.io/abelisboa`.
- The repository-provided `NetworkSliceInstance`,
  `NetworkSliceSubnetInstance`, and `TriSLAReservation` CRDs under
  [`apps/nasp-adapter/crds/`](apps/nasp-adapter/crds/).
- Prometheus Operator CRDs and a `monitoring` namespace if the default
  `ServiceMonitor` and `PrometheusRule` resources remain enabled.

The default main chart also renders compatibility workloads. BC-NSSMF and Besu
reference existing Secrets named `bc-nssmf-wallet` and
`trisla-besu-validator-key`; BC-NSSMF also references an external ConfigMap
named `trisla-bc-contract-address`. The repository does not currently provide
creation commands for these resources.

#### Local development

- Python 3.10 for the Portal backend, SEM-CSMF, Decision Engine, NASP Adapter,
  SLA-Agent, and Traffic Exporter
- Python 3.11 for ML-NSMF
- Node.js 20 for the Portal frontend
- Node.js 18 for the preserved earlier UI dashboard

Install dependencies from each component's `requirements.txt` or
`package.json`. The current core source does not require a Java application
runtime.

### Configuration

Start with [`helm/trisla/values.yaml`](helm/trisla/values.yaml), use
[`helm/trisla/values-nasp.yaml`](helm/trisla/values-nasp.yaml) for repository
image overrides, and configure the Portal separately through
[`helm/trisla-portal/values.yaml`](helm/trisla-portal/values.yaml).

| Setting | Scope | Current behavior |
| --- | --- | --- |
| `global.namespace` | Main chart | Workload namespace; default `trisla` |
| `global.imageRegistry` | Main chart | Image registry; default `ghcr.io/abelisboa` |
| `global.imagePullSecrets` | Main chart | Registry pull-secret references; empty by default |
| `network.interface`, `nodeIP`, `gateway` | Shared configuration | Environment-specific network coordinates; empty by default |
| `semCsmf.env.DECISION_ENGINE_URL` | SEM-CSMF | The chart supplies the in-cluster Decision Engine URL when empty |
| `decisionEngine.env.*` | Decision Engine | Admission thresholds and scoring controls |
| `naspAdapter.gate3gpp.*` | NASP Adapter | 3GPP gate enabled by default for `ns-1274485` and `ueransim` |
| `naspAdapter.capacityAccounting.*` | NASP Adapter | Capacity reservation and reconciliation enabled |
| `naspAdapter.prometheusUrl` | NASP Adapter | URL of the externally supplied Prometheus service |
| `naspAdapter.*Binding.enabled` | NASP Adapter | Slice-service binding enabled; other domain bindings disabled by default |
| `slaAgentLayer.env.KAFKA_ENABLED` | SLA-Agent | Kafka integration enabled by default |
| `slaAgentLayer.env.CLOSED_LOOP_ACTUATION_ENABLED` | SLA-Agent | Closed-loop execution disabled by default |
| `slaAgentLayer.env.CLOSED_LOOP_TRANSPORT_DRYRUN_ENABLED` | SLA-Agent | Transport dry-run enabled by default |
| `backend.env.SEM_CSMF_URL` | Portal backend | Consumed by the active submission path |
| `backend.env.ML_NSMF_URL`, `DECISION_ENGINE_URL` | Portal backend | Injected by the chart; the active path reaches these services through SEM-CSMF |
| `backend.env.BC_NSSMF_URL` | Portal backend | Injected but not read by the active compatibility client, which uses `http://trisla-bc-nssmf:8083` |
| `backend.env.SLA_AGENT_URL` | Portal backend | Injected but not used by active pipeline ingestion |
| `SLA_AGENT_PIPELINE_INGEST_URL` | Portal backend | Active pipeline endpoint; not exposed by the current chart and empty by default |
| `NASP_ADAPTER_BASE_URL` | Portal backend | Active NASP endpoint; not exposed by the chart and defaults to the in-cluster adapter service |
| `frontend.env.BACKEND_URL` | Portal frontend | Portal API base URL |

Do not store secret values in Helm values files.

### Deployment and compatibility notes

The repository's main chart deploys TriSLA application services and monitoring
custom resources. The Portal is packaged in a separate chart. External RAN,
transport, and 5GC infrastructure is not installed by the main chart, and the
chart does not deploy Prometheus, Grafana, OpenTelemetry Collector, Jaeger,
Loki, or Tempo workloads. Operators must provide the required domain and
observability infrastructure for their environment.

The repository implements the main control path with synchronous REST APIs,
structured JSON over HTTP, and Kubernetes service discovery. It also preserves
a compatibility path in which the Portal backend registers an SLA with
BC-NSSMF after successful NASP provisioning. In the current implementation,
that registration can gate subsequent SLA-Agent pipeline ingestion. BC-NSSMF,
Hyperledger Besu, and the earlier UI dashboard are repository compatibility
components; they are not components of the scientific architecture above.

The main Helm chart currently renders BC-NSSMF and the earlier UI dashboard
regardless of their `enabled` values, while Besu is conditionally rendered and
enabled by default. Review rendered manifests before deployment. See the
[application index](apps/README.md) and [Helm chart index](helm/README.md) for
current component and packaging boundaries.

Run commands from the repository root.

### 1. Validate the charts

```bash
helm lint ./helm/trisla -f ./helm/trisla/values-nasp.yaml
helm lint ./helm/trisla-portal
helm template trisla ./helm/trisla \
  -f ./helm/trisla/values-nasp.yaml \
  > /tmp/trisla-rendered.yaml
helm template trisla-portal ./helm/trisla-portal \
  > /tmp/trisla-portal-rendered.yaml
```

Inspect the rendered main manifest before applying it. Its defaults include
BC-NSSMF, Besu, the earlier UI dashboard, and Kafka resources.

### 2. Install the NASP CRDs

```bash
kubectl apply -f ./apps/nasp-adapter/crds/networksliceinstances.trisla.io.yaml
kubectl apply -f ./apps/nasp-adapter/crds/networkslicesubnetinstances.trisla.io.yaml
kubectl apply -f ./apps/nasp-adapter/crds/trislareservations.trisla.io.yaml
```

Provide registry access, external domain endpoints, namespaces, and monitoring
prerequisites. Supply the compatibility Secrets and ConfigMap described above
if the corresponding default resources remain in the rendered manifest.

### 3. Install the main services and Portal

```bash
helm upgrade --install trisla ./helm/trisla \
  --namespace trisla \
  --create-namespace \
  -f ./helm/trisla/values-nasp.yaml

helm upgrade --install trisla-portal ./helm/trisla-portal \
  --namespace trisla
```

The Portal values present in `helm/trisla/values-nasp.yaml` are not consumed by
the main chart. Deploy the Portal with its separate chart.

## Running and Validation

Check the deployed resources and Helm releases:

```bash
kubectl get pods -n trisla
kubectl get services -n trisla
helm status trisla -n trisla
helm status trisla-portal -n trisla
```

Reach the Portal through NodePort `32001` and the backend through NodePort
`32002`, subject to cluster networking:

```bash
NODE_ADDRESS="replace-with-node-address"
curl "http://${NODE_ADDRESS}:32002/health"
curl "http://${NODE_ADDRESS}:32002/nasp/diagnostics"
```

Submit an SLA request through the Portal API. The example follows the
implemented request model and repository route tests:

```bash
SUBMIT_PAYLOAD='{"template_id":"urllc-template-001","form_values":{"latency":5,"reliability":99.999},"tenant_id":"default"}'
curl -X POST "http://${NODE_ADDRESS}:32002/api/v1/sla/submit" \
  -H 'Content-Type: application/json' \
  -d "${SUBMIT_PAYLOAD}"
```

Use the SLA identifier returned by the API to query status and metrics:

```bash
SLA_ID="replace-with-returned-sla-id"
curl "http://${NODE_ADDRESS}:32002/api/v1/sla/status/${SLA_ID}"
curl "http://${NODE_ADDRESS}:32002/api/v1/sla/metrics/${SLA_ID}"
```

An `ACCEPT` outcome requests NASP instantiation. After successful provisioning,
the current compatibility path attempts BC-NSSMF registration and invokes
SLA-Agent pipeline ingestion only when orchestration and blockchain
registration both succeed. Use the API response and NASP/Portal diagnostics to
verify the workflow. External RAN, TN, and 5GC provisioning requires
installation-specific validation.

The repository does not provide a universal uninstall script. Review installed
resources and Helm release data before choosing environment-specific cleanup
commands.

### Validation

The Helm lint and render commands in the Installation section provide static
chart validation. Runtime checks after deployment:

```bash
NODE_ADDRESS="replace-with-node-address"
kubectl get pods -n trisla
kubectl get services -n trisla
curl "http://${NODE_ADDRESS}:32002/health"
curl "http://${NODE_ADDRESS}:32002/nasp/diagnostics"
```

Portal route checks are provided in
[`apps/portal-backend/test_backend_routes.sh`](apps/portal-backend/test_backend_routes.sh)
and [`apps/portal-backend/test_backend.sh`](apps/portal-backend/test_backend.sh).
Component tests are colocated with their source and require each component's
declared development dependencies.

## Observability

| Surface | Purpose and current boundary |
| --- | --- |
| Component `/health` routes | Kubernetes probes and service health checks |
| Component `/metrics` routes | Prometheus-format application metrics |
| NASP metrics service | NASP and multidomain measurements through `trisla-nasp-adapter-metrics` |
| Traffic Exporter | Traffic telemetry through `trisla-traffic-exporter:9105/metrics` |
| `ServiceMonitor` resources | Prometheus Operator discovery in the `monitoring` namespace |
| `PrometheusRule` | TriSLA recording rules in the `monitoring` namespace |
| Portal Prometheus proxy | Mounted under `/api/v1/prometheus` |
| Portal Loki and Tempo modules | Code and configuration exist, but the routers are not mounted by the current Portal backend |

The main chart renders monitoring custom resources but does not install their
operators or storage/query backends.

## Troubleshooting

| Symptom | Check | Resolution |
| --- | --- | --- |
| Helm reports unknown `ServiceMonitor` or `PrometheusRule` kinds | Run `kubectl api-resources` | Provide Prometheus Operator CRDs or render a configuration appropriate to the cluster |
| Portal is absent after installing the main chart | Run `helm status trisla-portal -n trisla` | Install `helm/trisla-portal` separately |
| Portal diagnostics report unreachable services | Inspect `/nasp/diagnostics`, Portal logs, and effective service URLs | Correct service discovery or endpoint configuration and verify downstream health |
| BC-NSSMF or Besu cannot start | Inspect pod events and referenced Secrets/ConfigMaps | Provide the required compatibility resources or customize the rendered manifests |
| Disabling BC-NSSMF or the earlier UI still renders resources | Inspect `helm template` output | Treat those flags as ineffective in the current chart and review the resources before installation |
| NASP does not mutate a domain | Review binding values, controller reachability, and dry-run settings | Enable and configure the intended external integration |
| Metrics surfaces have no data | Check the configured observability backend URL and discovery | Provide the external backend and correct its endpoint |

## Repository Structure and Documentation

| Path | Purpose |
| --- | --- |
| [`apps/`](apps/README.md) | Application services, Portal, exporters, and compatibility components |
| [`datasets/`](datasets/README.md) | Public evaluation dataset and integrity information |
| [`docs/`](docs/README.md) | Architecture, component, interface, Portal, and observability documentation |
| [`helm/`](helm/README.md) | Main, Portal, and preserved compatibility Helm charts |
| [`LICENSE`](LICENSE) | Apache License 2.0 |

Tests are colocated with individual components. The repository does not provide
a root Makefile or a single bootstrap script.

The linked directory READMEs are the primary entry points for application,
dataset, technical, and Helm documentation.

## Dataset

The repository publishes the consolidated TriSLA evaluation dataset in
Parquet and CSV formats. See the [dataset documentation](datasets/README.md)
for its schema, coverage, and provenance.

| Artifact | SHA-256 |
| --- | --- |
| `datasets/trisla_master_dataset_v2.parquet` | `ab91d78557cab21a80bb460d000754827c6a242d74ea49ec8190d185e6f67631` |
| `datasets/trisla_master_dataset_v2.csv` | `e97ad9f9a63c24cbcf6516054da3b2369e8d23624abfc33348175f05c5a57b71` |

Verify the artifacts locally:

```bash
sha256sum datasets/trisla_master_dataset_v2.parquet \
  datasets/trisla_master_dataset_v2.csv
```

## Citation

If you use TriSLA in research, cite:

> Abel J. R. Lisboa, Gustavo Z. Bruno, and Cristiano B. Both. “TriSLA: A Preventive and Closed-Loop SLA-Aware Architecture for Explainable Multidomain Admission in 5G Networks.”

Venue, DOI, volume, issue, pages, year, and final publication status are not
currently available in the article artifact. Update the citation when verified
bibliographic metadata becomes available.

## License

Licensed under the Apache License 2.0. See [LICENSE](LICENSE).
