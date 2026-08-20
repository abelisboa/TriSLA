# TriSLA

TriSLA is a Kubernetes-oriented platform for SLA intake, semantic interpretation, ML-assisted feasibility inference, preventive admission decisions, multidomain provisioning, telemetry, and runtime assurance across RAN, transport, and 5GC domains.

This README documents behavior supported by the repository at the current revision. Source code and active Helm templates take precedence over historical descriptions.

## Architecture

| Tier | Active component | Responsibility |
|---|---|---|
| Intake | SLA Intake Gateway (Portal frontend and backend) | Accept an SLA request, coordinate the service workflow, and expose status and diagnostics |
| Semantic | SEM-CSMF | Interpret a request, normalize SLA terms, create intents, and invoke admission evaluation |
| Inference | ML-NSMF | Produce feasibility predictions used by the decision path |
| Decision | Decision Engine | Combine request, prediction, policy, and telemetry inputs into an explainable admission result |
| Provisioning | NASP Adapter | Apply admission gates, account for capacity, and coordinate RAN, transport, and 5GC bindings |
| Assurance | SLA-Agent Layer | Ingest pipeline events, evaluate runtime assurance, and audit closed-loop actions |
| Telemetry | NASP metrics and traffic exporters | Export service and multidomain signals for monitoring |

The approved current scientific-core workflow is:

~~~text
SLA Intake Gateway
  -> SEM-CSMF
     -> Decision Engine
        -> ML-NSMF feasibility inference
     -> NASP Adapter after ACCEPT
        -> configured RAN, transport, and 5GC integrations
     -> SLA-Agent Layer for runtime assurance
~~~

The current implementation also retains this compatibility-affected path after successful NASP provisioning:

~~~text
NASP provisioning succeeds
  -> Portal backend registers the SLA with BC-NSSMF
     -> registration succeeds: Portal may ingest the pipeline event into SLA-Agent
     -> registration fails: Portal skips SLA-Agent ingestion and marks the lifecycle failed
~~~

BC-NSSMF is therefore operationally active in the current Portal workflow even though it is not part of the approved scientific core. REST is the authoritative request path. Kafka support exists for selected component event paths and is configuration-dependent.

### Implementation boundary

The approved current core is the intake, semantic, inference, decision, provisioning, assurance, and telemetry path above. The following legacy or compatibility components remain in the repository and active deployment path, but they are not part of the approved current scientific core:

| Compatibility component | Repository and deployment evidence | Current operational status |
|---|---|---|
| BC-NSSMF | apps/bc-nssmf and unconditional main-chart Deployment/Service templates | Rendered by default and called by the Portal after successful NASP provisioning |
| Hyperledger Besu and Solidity material | apps/besu, apps/bc-nssmf/src/contracts, and conditionally rendered Besu templates | Besu is enabled by default and supports the BC-NSSMF compatibility path |
| Legacy UI dashboard | apps/ui-dashboard and unconditional main-chart Deployment/Service templates | Rendered by default; distinct from the current Portal chart |

The main Helm chart still renders BC-NSSMF and the legacy UI even when their respective enabled values are set to false because their Deployment and Service templates are not conditionally guarded. Besu is conditionally guarded. The Portal backend still checks BC-NSSMF, attempts SLA registration after successful provisioning, and gates SLA-Agent pipeline ingestion on successful blockchain registration.

A repository-supported Helm profile that installs only the approved current core is **EVIDENCE NOT AVAILABLE**. Review rendered manifests before deployment.

## Components

Service names below assume the release name used in the installation examples: trisla.

| Component | Source | Runtime | Kubernetes service / port | Health and metrics | Principal implemented API |
|---|---|---|---|---|---|
| Portal frontend | [apps/portal-frontend](apps/portal-frontend) | Node.js 20, Next.js 15 | trisla-portal-frontend:80; NodePort 32001; container 3000 | GET / | Browser interface |
| Portal backend / SLA Intake Gateway | [apps/portal-backend](apps/portal-backend) | Python 3.10, FastAPI | trisla-portal-backend:8001; NodePort 32002 | GET /health, GET /nasp/diagnostics, GET /metrics | POST /api/v1/sla/interpret, POST /api/v1/sla/submit, GET /api/v1/sla/status/{sla_id}, GET /api/v1/sla/metrics/{sla_id}, POST /api/v1/sla/revalidate-telemetry |
| SEM-CSMF | [apps/sem-csmf](apps/sem-csmf) | Python 3.10, FastAPI | trisla-sem-csmf:8080 | GET /health, GET /metrics | POST /api/v1/interpret, POST /api/v1/intents, GET /api/v1/intents/{intent_id} |
| ML-NSMF | [apps/ml-nsmf](apps/ml-nsmf) | Python 3.11, FastAPI | trisla-ml-nsmf:8081 | GET /health, GET /metrics | POST /api/v1/predict |
| Decision Engine | [apps/decision-engine](apps/decision-engine) | Python 3.10, FastAPI | trisla-decision-engine:8082 | GET /health, GET /metrics | POST /evaluate |
| NASP Adapter | [apps/nasp-adapter](apps/nasp-adapter) | Python 3.10, FastAPI and Kubernetes client | trisla-nasp-adapter:8085 | GET /health, GET /api/v1/nasp/metrics; /metrics is instrumented | POST /api/v1/nsi/instantiate, GET /api/v1/metrics/multidomain, 3GPP gate and slice-binding APIs |
| SLA-Agent Layer | [apps/sla-agent-layer](apps/sla-agent-layer) | Python 3.10, FastAPI | trisla-sla-agent-layer:8084 | GET /health, GET /metrics | POST /api/v1/ingest/pipeline-event, POST /api/v1/runtime-assurance/evaluate, actuation lifecycle APIs |
| Traffic Exporter | [apps/traffic-exporter](apps/traffic-exporter) | Python 3.10, FastAPI | trisla-traffic-exporter:9105 | GET /health, GET /metrics | Telemetry exporter |
| Kafka | [apps/kafka](apps/kafka) | Containerized broker | kafka:9092 | No repository health endpoint | Optional/conditional event transport |

All listed workloads target the trisla namespace by default. The main chart is [helm/trisla](helm/trisla); the Portal uses the separate [helm/trisla-portal](helm/trisla-portal) chart. Container build definitions are colocated with their application sources.

## Repository structure

~~~text
trisla_public/
├── apps/                    # Services, portal, exporters, and preserved extensions
├── datasets/                # Versioned public master dataset and provenance
├── docs/                    # Component, interface, portal, and observability documentation
├── helm/
│   ├── trisla/              # Main service and telemetry-resource chart
│   ├── trisla-portal/       # Portal frontend/backend chart
│   └── trisla-besu/         # Separate preserved Besu chart
├── LICENSE                  # Apache License 2.0
└── README.md                # Repository entry point
~~~

Tests are colocated inside component directories. The repository has no root Makefile or single bootstrap script.

## Requirements

### Mandatory

#### Core prerequisites

- A Kubernetes cluster and configured kubectl context. A minimum Kubernetes version is **EVIDENCE NOT AVAILABLE**.
- Helm 3; the charts use Helm chart API v2. A minimum Helm version is **EVIDENCE NOT AVAILABLE**.
- Cluster access to the configured container registry. Default images are hosted under ghcr.io/abelisboa.
- The repository-provided NetworkSliceInstance, NetworkSliceSubnetInstance, and TriSLAReservation CRDs under apps/nasp-adapter/crds. NASP creates these custom resources during provisioning and capacity accounting.
- Prometheus Operator CRDs and a monitoring namespace when the default ServiceMonitor and PrometheusRule resources are rendered.

#### Compatibility-workload prerequisites

The default main chart also renders BC-NSSMF and Besu even though they are not part of the approved scientific core. Those compatibility workloads reference the existing Secrets bc-nssmf-wallet and trisla-besu-validator-key. BC-NSSMF also references an external ConfigMap named trisla-bc-contract-address. Repository-supported creation procedures for these three resources are **EVIDENCE NOT AVAILABLE**.

The repository does not define a mandatory container-runtime product.

### Local development

- Python 3.10 for Portal backend, SEM-CSMF, Decision Engine, NASP Adapter, SLA-Agent Layer, and Traffic Exporter.
- Python 3.11 for ML-NSMF.
- Node.js 20 for the Portal frontend.
- Node.js 18 is used by the preserved legacy UI dashboard build.

Install Python and Node dependencies from the requirements.txt and package.json files in each component. No Java application runtime is required by the current core source.

### Optional or external infrastructure

- Kafka is deployed by the default main chart, although ML Kafka consumption is disabled by default.
- Prometheus, Grafana, OpenTelemetry Collector, Jaeger, Loki, and Tempo are integration targets or configuration surfaces; the main chart does not deploy their workloads.
- ONOS, Mininet, free5GC, UERANSIM, RAN elements, and transport/core controllers are external or testbed integrations. They are not installed by the main chart.

## Configuration

Start with [helm/trisla/values.yaml](helm/trisla/values.yaml), use [helm/trisla/values-nasp.yaml](helm/trisla/values-nasp.yaml) for repository image overrides, and configure the Portal separately in [helm/trisla-portal/values.yaml](helm/trisla-portal/values.yaml).

| Parameter | Component | Effective classification | Current behavior and default |
|---|---|---|---|
| global.namespace | Main chart | ACTIVE | Workload namespace; trisla |
| global.imageRegistry | Main chart | ACTIVE | Default image registry; ghcr.io/abelisboa |
| global.imagePullSecrets | Main chart | ACTIVE | Registry pull-secret references; empty |
| network.interface / nodeIP / gateway | Shared configuration | ACTIVE | Host/testbed network coordinates; empty |
| semCsmf.env.DECISION_ENGINE_URL | SEM-CSMF | ACTIVE | Decision service override; the chart supplies an in-cluster URL when the value is empty |
| decisionEngine.env.* | Decision Engine | ACTIVE | Thresholds and runtime scoring controls; see values.yaml |
| naspAdapter.gate3gpp.* | NASP Adapter | ACTIVE | 3GPP gate enabled; target namespaces ns-1274485 and ueransim |
| naspAdapter.capacityAccounting.* | NASP Adapter | ACTIVE | Capacity reservation and reconciliation enabled |
| naspAdapter.prometheusUrl | NASP Adapter | ACTIVE | External Prometheus service URL |
| naspAdapter.*Binding.enabled | NASP Adapter | ACTIVE | Slice-service binding true; other domain bindings false |
| slaAgentLayer.env.KAFKA_ENABLED | SLA-Agent | ACTIVE | Kafka integration true |
| slaAgentLayer.env.CLOSED_LOOP_ACTUATION_ENABLED | SLA-Agent | ACTIVE | Closed-loop execution false |
| slaAgentLayer.env.CLOSED_LOOP_TRANSPORT_DRYRUN_ENABLED | SLA-Agent | ACTIVE | Transport dry-run true |
| backend.env.SEM_CSMF_URL | Portal backend | ACTIVE | Consumed by the active submit path; http://trisla-sem-csmf:8080 |
| backend.env.ML_NSMF_URL | Portal backend | INDIRECT; INJECTED_BUT_NOT_CONSUMED_BY_ACTIVE_PATH | The chart injects it, but the active submit path reaches ML-NSMF indirectly through SEM-CSMF and Decision Engine |
| backend.env.DECISION_ENGINE_URL | Portal backend | INDIRECT; INJECTED_BUT_NOT_CONSUMED_BY_ACTIVE_PATH | The chart injects it, but the active submit path reaches the Decision Engine through SEM-CSMF |
| backend.env.BC_NSSMF_URL | Portal backend | INJECTED_BUT_NOT_CONSUMED_BY_ACTIVE_PATH | The chart injects it, but the active compatibility client does not read it |
| BC-NSSMF runtime URL | Portal backend | HARDCODED_COMPATIBILITY | The active client uses http://trisla-bc-nssmf:8083 directly |
| backend.env.SLA_AGENT_URL | Portal backend | INJECTED_BUT_NOT_CONSUMED_BY_ACTIVE_PATH | The chart injects it, but active pipeline ingestion uses SLA_AGENT_PIPELINE_INGEST_URL |
| SLA_AGENT_PIPELINE_INGEST_URL | Portal backend | ACTIVE; NOT_EXPOSED_BY_CHART | Empty by default; when unset, ingestion is skipped unless SLA_AGENT_REQUIRED_FOR_ACCEPT is true |
| NASP_ADAPTER_BASE_URL | Portal backend | ACTIVE; NOT_EXPOSED_BY_CHART | Defaults to http://trisla-nasp-adapter.trisla.svc.cluster.local:8085 |
| frontend.env.BACKEND_URL | Portal frontend | ACTIVE | Portal API base URL; http://trisla-portal-backend:8001/api/v1 |

Do not place secret values in values files. The default chart supports image-pull credentials and references external resources for preserved blockchain compatibility workloads.

## Installation

Run all commands from the repository root.

### 1. Preflight the charts

~~~bash
helm lint ./helm/trisla -f ./helm/trisla/values-nasp.yaml
helm lint ./helm/trisla-portal
helm template trisla ./helm/trisla -f ./helm/trisla/values-nasp.yaml > /tmp/trisla-rendered.yaml
helm template trisla-portal ./helm/trisla-portal > /tmp/trisla-portal-rendered.yaml
~~~

Inspect the rendered main manifest before applying it. In particular, its defaults include preserved BC-NSSMF, Besu, legacy UI, and Kafka resources.

### 2. Install core CRDs and satisfy core prerequisites

Apply the repository-provided NASP CRDs:

~~~bash
kubectl apply -f ./apps/nasp-adapter/crds/networksliceinstances.trisla.io.yaml
kubectl apply -f ./apps/nasp-adapter/crds/networkslicesubnetinstances.trisla.io.yaml
kubectl apply -f ./apps/nasp-adapter/crds/trislareservations.trisla.io.yaml
~~~

Provide registry access, configure the external domain endpoints and namespaces, and ensure Prometheus Operator CRDs and the monitoring namespace are available if the default monitoring resources remain enabled.

### 3. Satisfy compatibility-workload prerequisites

The default main chart renders the BC-NSSMF and Besu compatibility workloads. They reference bc-nssmf-wallet, trisla-besu-validator-key, and trisla-bc-contract-address. Repository-supported creation commands for those Secrets and ConfigMap are **EVIDENCE NOT AVAILABLE**. These resources belong to the legacy compatibility path, not the approved scientific core.

### 4. Install the main services and Portal

~~~bash
helm upgrade --install trisla ./helm/trisla   --namespace trisla   --create-namespace   -f ./helm/trisla/values-nasp.yaml

helm upgrade --install trisla-portal ./helm/trisla-portal   --namespace trisla
~~~

The Portal values present in helm/trisla/values-nasp.yaml are not consumed by the main chart; install helm/trisla-portal separately.

## Running TriSLA

Check the deployed resources:

~~~bash
kubectl get pods -n trisla
kubectl get services -n trisla
helm status trisla -n trisla
helm status trisla-portal -n trisla
~~~

Reach the Portal through NodePort 32001 and the backend through NodePort 32002, subject to cluster networking:

~~~bash
NODE_ADDRESS="replace-with-node-address"
curl "http://${NODE_ADDRESS}:32002/health"
curl "http://${NODE_ADDRESS}:32002/nasp/diagnostics"
~~~

Submit an SLA request through the implemented Portal API. This payload is taken from [apps/portal-backend/test_backend.sh](apps/portal-backend/test_backend.sh) and conforms to the request model in [apps/portal-backend/src/schemas/sla.py](apps/portal-backend/src/schemas/sla.py):

~~~bash
SUBMIT_PAYLOAD='{"template_id":"urllc-template-001","form_values":{"latency":5,"reliability":99.999},"tenant_id":"default"}'
curl -X POST "http://${NODE_ADDRESS}:32002/api/v1/sla/submit"   -H 'Content-Type: application/json'   -d "${SUBMIT_PAYLOAD}"
~~~

The response supplies identifiers and the admission outcome. Set the returned SLA identifier before requesting status and metrics:

~~~bash
SLA_ID="replace-with-returned-sla-id"
curl "http://${NODE_ADDRESS}:32002/api/v1/sla/status/${SLA_ID}"
curl "http://${NODE_ADDRESS}:32002/api/v1/sla/metrics/${SLA_ID}"
~~~

An ACCEPT result causes the Portal backend to request NASP instantiation. After successful provisioning, the current compatibility path attempts BC-NSSMF registration. The Portal invokes SLA-Agent pipeline ingestion only when orchestration and blockchain registration both succeed. Verify provisioning with the response and NASP/Portal diagnostics; a single universal command proving external RAN, transport, and 5GC provisioning is **EVIDENCE NOT AVAILABLE**.

A repository-owned uninstall or teardown script is **EVIDENCE NOT AVAILABLE**. If removal is intended, review the installed resources and Helm release data before choosing environment-specific cleanup commands.

## Observability

| Surface | Purpose | Deployment and access | Evidence |
|---|---|---|---|
| Service /health routes | Liveness and readiness | Component HTTP ports; used by Kubernetes probes | Application main modules and Helm deployments |
| Service /metrics routes | Prometheus-format application metrics | Component HTTP ports | FastAPI instrumentation in component sources |
| NASP metrics service | NASP and multidomain metrics | trisla-nasp-adapter-metrics | Main Helm chart |
| Traffic Exporter | Traffic telemetry | trisla-traffic-exporter:9105/metrics | Source and main Helm chart |
| ServiceMonitor resources | Prometheus Operator discovery | monitoring namespace | Main Helm chart |
| PrometheusRule | TriSLA recording rules | monitoring namespace | helm/trisla/templates/prometheusrule-trisla-recording.yaml |
| Portal Prometheus proxy | Prometheus query surface | Mounted under /api/v1/prometheus | apps/portal-backend/src/main.py and apps/portal-backend/src/routers/prometheus.py |
| Portal Loki and Tempo code | Unmounted configuration/code surfaces | No active Portal route | Router and service modules exist, but apps/portal-backend/src/main.py does not mount them |

The repository contains configuration references for Prometheus, Grafana, OpenTelemetry, Loki, Tempo, and tracing. Their presence does not prove that those backends are installed or active. The main chart creates monitoring custom resources, but not Prometheus, Grafana, or an OpenTelemetry Collector workload. In the current Portal backend, Prometheus routes are mounted; Loki and Tempo router modules are not.

## Validation

Static deployment validation:

~~~bash
helm lint ./helm/trisla -f ./helm/trisla/values-nasp.yaml
helm lint ./helm/trisla-portal
helm template trisla ./helm/trisla -f ./helm/trisla/values-nasp.yaml > /tmp/trisla-rendered.yaml
helm template trisla-portal ./helm/trisla-portal > /tmp/trisla-portal-rendered.yaml
~~~

Runtime validation after deployment:

~~~bash
NODE_ADDRESS="replace-with-node-address"
kubectl get pods -n trisla
kubectl get services -n trisla
curl "http://${NODE_ADDRESS}:32002/health"
curl "http://${NODE_ADDRESS}:32002/nasp/diagnostics"
~~~

Portal route checks are provided in [apps/portal-backend/test_backend_routes.sh](apps/portal-backend/test_backend_routes.sh) and [apps/portal-backend/test_backend.sh](apps/portal-backend/test_backend.sh). Component unit and integration tests are colocated with their source; install the component's declared development dependencies before invoking its test runner.

## Troubleshooting

| Symptom | Repository-supported likely cause | Check | Action |
|---|---|---|---|
| Helm reports unknown ServiceMonitor or PrometheusRule kinds | Prometheus Operator CRDs are unavailable | kubectl api-resources | Install/provide the operator CRDs or render a values profile appropriate to the cluster |
| Portal is absent after installing the main chart | Portal is a separate chart | helm status trisla-portal -n trisla | Install helm/trisla-portal |
| Portal diagnostics report downstream services as unreachable | /nasp/diagnostics returns per-service reachability entries, including failures, while retaining a successful HTTP response | Inspect the diagnostics response, Portal logs, and effective service URLs | Correct service DNS/endpoints and confirm downstream health |
| Main install cannot start BC-NSSMF or Besu | Default templates reference existing wallet/validator secrets | Inspect pod events and secret references in values.yaml | Supply the required secrets or review and customize the rendered extension resources |
| Disabling bcNssmf or uiDashboard still renders resources | Their templates do not honor the enabled values | Inspect helm template output | Treat the flag as ineffective in the current chart; do not assume a core-only profile |
| NASP does not mutate a domain | The corresponding binding is disabled, an external controller is unavailable, or dry-run is enabled | Review NASP and SLA-Agent values and diagnostics | Configure the intended external integration explicitly |
| Metrics UI/proxy has no data | A referenced observability backend is not deployed or reachable | Check configured backend URL and service discovery | Provide the external backend and correct its URL |

## Dataset

The public dataset is documented in [datasets/README.md](datasets/README.md).

| Artifact | SHA-256 |
|---|---|
| datasets/trisla_master_dataset_v2.parquet | ab91d78557cab21a80bb460d000754827c6a242d74ea49ec8190d185e6f67631 |
| datasets/trisla_master_dataset_v2.csv | e97ad9f9a63c24cbcf6516054da3b2369e8d23624abfc33348175f05c5a57b71 |

Verify locally with sha256sum datasets/trisla_master_dataset_v2.parquet datasets/trisla_master_dataset_v2.csv.

## Documentation

- [Documentation index](docs/README.md)
- [Component interfaces](docs/modules/interfaces.md)
- [Portal](docs/portal/README.md)
- [SEM-CSMF](docs/sem-csmf/README.md)
- [ML-NSMF](docs/ml-nsmf/README.md)
- [Decision Engine](docs/decision-engine/README.md)
- [NASP Adapter](docs/nasp-adapter/README.md)
- [SLA-Agent](docs/sla-agent/README.md)
- [Observability](docs/observability/OBSERVABILITY.md)
- [Telemetry module](docs/modules/telemetry.md)

Documents about BC-NSSMF or blockchain describe preserved extension/history material and are not canonical descriptions of the approved current core.

## Scientific publication

The TriSLA architecture and its scientific evaluation are described in the associated scientific publication.

Publication metadata pending.

Complete citation metadata will be added when the publication metadata is available.

## License

Licensed under the Apache License 2.0. See [LICENSE](LICENSE).
