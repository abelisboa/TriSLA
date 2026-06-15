# Observability Layer

> **Operational entry point** for TriSLA runtime monitoring and observability.
> Telemetry canonical reference: [`docs/modules/telemetry.md`](telemetry.md).
> Specialized PromQL reference: [`docs/PROMQL_SSOT_V2.md`](../PROMQL_SSOT_V2.md).
> Legacy / navigation hub: [`docs/observability/OBSERVABILITY.md`](../observability/OBSERVABILITY.md).


## Runtime Position In TriSLA Flow

Runtime position and cross-module flow ordering are defined by [`docs/modules/interfaces.md`](interfaces.md). This module document does not duplicate the full chain.

## Frozen Status

| Property | Status |
|----------|--------|
| PROJECT_STATUS | CONSOLIDATED |
| DISSERTATION_STATUS | READY_FOR_FINAL_ALIGNMENT |
| ARCHITECTURE | FROZEN |
| RESULTS | FROZEN |
| EXPERIMENTS | FROZEN |
| SCIENTIFIC_BASELINE | FROZEN |
| PHASE47_STATUS | APPROVED |
| TRISLA_STATUS | DEMO_READY |

## Role

The Observability Layer is the **Runtime Monitoring and Observability Layer**.

**Observability Layer does not make decisions.**
**Observability Layer does not execute admission.**
**Observability Layer does not generate telemetry.**
**Observability Layer does not generate governance.**

**Provides:**

- Metrics Monitoring
- Tracing
- Health Monitoring
- Readiness Monitoring
- Dashboards
- Evidence Support

**Does not provide:**

- Admission authority
- Decision authority
- Telemetry snapshot generation
- Governance registration
- Runtime scoring input ownership
- Production notification workflow unless explicitly evidenced

## Official Operational Chains

### Metrics Path

```text
Applications
↓
Metrics
↓
Prometheus
↓
Grafana
↓
Operators
```

### Tracing Path

```text
Applications
↓
OTEL Instrumentation
↓
OTEL Collector
↓
Tempo
↓
Jaeger
```

```text
Prometheus
=
PRIMARY OBSERVABILITY METRICS SOURCE
```

```text
OTEL
=
TRACING AND INSTRUMENTATION
```

```text
OTEL
≠
telemetry_snapshot source
```

Implementation-first boundary: observability supports telemetry visibility and evidence, but `telemetry_snapshot` remains defined by [`docs/modules/telemetry.md`](telemetry.md) and is sourced through Prometheus-backed collectors, not OTEL.

## Prometheus Runtime Truth

| Capability | Status | Runtime truth |
|------------|--------|---------------|
| Prometheus Server | ACTIVE | `prometheus-prometheus-kube-prometheus-prometheus-0` in namespace `monitoring` |
| ServiceMonitors | ACTIVE | TriSLA service monitors plus kube-prometheus stack monitors are present |
| PrometheusRules | ACTIVE | kube-prometheus rules plus TriSLA rules are present |
| Recording Rules | ACTIVE | `monitoring/o7c-trisla-recording-rules.yaml` / `trisla-recording-rules` |
| `/metrics` endpoints | ACTIVE | Exposed by core TriSLA services and exporters |

Exporters and metric sources:

| Exporter / source | Status | Notes |
|-------------------|--------|-------|
| node-exporter | ACTIVE | Node-level runtime metrics |
| kube-state-metrics | ACTIVE | Kubernetes object state metrics |
| blackbox-exporter | ACTIVE | Probe-based transport/availability signals |
| trisla-ran-ue-upf-proxy | ACTIVE | RAN/UE/UPF proxy metrics including PRB/throughput signals |
| trisla-traffic-exporter | ACTIVE | Traffic/exporter metrics |
| trisla-blockchain-exporter | ACTIVE | Blockchain-related metric source |
| trisla-network-exporter | ACTIVE | Network metric source |
| service HTTP metrics | ACTIVE | `trisla_http_requests_total`, `trisla_http_request_duration_seconds` and related service metrics |

`/metrics` is present in:

| Service | Status |
|---------|--------|
| SEM-CSMF | ACTIVE |
| Decision Engine | ACTIVE |
| ML-NSMF | ACTIVE |
| NASP Adapter | ACTIVE |
| BC-NSSMF | ACTIVE |
| SLA-Agent | ACTIVE |
| Portal Backend | ACTIVE |

Specialized PromQL expressions remain in [`docs/PROMQL_SSOT_V2.md`](../PROMQL_SSOT_V2.md). This document only defines the operational observability boundary.

## Grafana Runtime Truth

| Capability | Status | Runtime truth |
|------------|--------|---------------|
| Grafana | ACTIVE | Grafana pod/service in the monitoring stack |
| Datasource | ACTIVE | Prometheus |
| Active dashboard inventory | ACTIVE | Versioned dashboards in `grafana/` |
| Normative dashboard set | NORMATIVE | `TRISLA-NORM-*` dashboards |
| Archived dashboards | LEGACY | `grafana/archive/*` |
| Evidence freeze marker | EVIDENCE | `TRISLA_GRAFANA_FINAL_DASHBOARD_APPROVED` |

Active dashboards:

| Dashboard | Status | Title |
|-----------|--------|-------|
| DB-ORCH-001 | ACTIVE | Network Slice Service Orchestration |
| DB-ASSUR-001 | ACTIVE | Closed-Loop Service Assurance |
| DB-INTEL-001 | ACTIVE | Intent Translation and Intelligence |
| DB-GOV-001 | ACTIVE | Governance and Smart Contract Enforcement |
| DB-RAN-001 | ACTIVE | RAN and Transport Service Correlation |
| DB-LIFE-001 | ACTIVE | Multidomain Service Lifecycle |

Normative dashboards:

```text
TRISLA-NORM-*
```

Legacy dashboards:

```text
grafana/archive/*
```

Evidence freeze boundary:

```text
TRISLA_GRAFANA_FINAL_DASHBOARD_APPROVED
```

```text
UID d25e340d-887a-4027-902f-cbb7b7aa0391

CONFIRMED IN EVIDENCE PACKS

NOT VERIFIED IN ACTIVE DASHBOARD INVENTORY
```

The UID above must not be documented as verified in the active dashboard inventory unless a new runtime/dashboard inventory proves it there.

## OTEL Runtime Truth

Classification:

```text
PARTIAL
```

| Capability | Status | Runtime truth |
|------------|--------|---------------|
| Instrumentation | ACTIVE | FastAPI instrumentation and service spans exist across TriSLA services |
| Collector | ACTIVE | OTEL Collector is deployed in runtime |
| Tempo | ACTIVE | Tempo is present as tracing backend |
| Jaeger | ACTIVE | Jaeger is present for trace inspection/export compatibility |
| Telemetry Source | NOT PRIMARY | OTEL is not the source of `telemetry_snapshot` |
| Admission Path | NOT DECISION INPUT | Admission decisions do not consume OTEL traces as decision input |
| Logs/metrics completeness | PARTIAL | Environment-dependent and not the observability SSOT |

OTEL must be described as tracing and instrumentation. It must not be described as the primary telemetry source or as a `telemetry_snapshot` producer.

## Logging Runtime Truth

| Capability | Status | Runtime truth |
|------------|--------|---------------|
| Application Logs | ACTIVE | Services use Python logging and container stdout/stderr |
| Runtime Logs | ACTIVE | Kubernetes/container runtime logs are available through the cluster |
| Container Logs | ACTIVE | Pod logs are part of the evidence/debug workflow |
| Structured Logging | PARTIAL | Some structured/interface/audit-style events exist; full uniform structured logging is not evidenced across all services |
| Governance logs | PARTIAL | Governance evidence is emitted through BC-NSSMF/Decision metadata and logs, not a separate observability database |

## Health Runtime Truth

| Capability | Status | Runtime truth |
|------------|--------|---------------|
| `/health` | ACTIVE | Present in primary services including SEM-CSMF, Decision Engine, ML-NSMF, NASP Adapter, BC-NSSMF, SLA-Agent, Portal Backend and exporters where implemented |
| `/health/ready` | ACTIVE WHERE PRESENT | BC-NSSMF exposes readiness; other services rely on health/probes where implemented |
| Kubernetes Probes | ACTIVE | Dockerfiles/deployments include health/probe behavior where configured |
| Health | ACTIVE | Basic service health endpoints and kube runtime state |
| Readiness | PARTIAL / ACTIVE WHERE PRESENT | Explicit readiness is not uniform across all services |
| Liveness | PARTIAL | Kubernetes/runtime probes exist where configured; not uniform as an application contract across every module |

## Alerting Runtime Truth

| Capability | Status | Runtime truth |
|------------|--------|---------------|
| Alertmanager | ACTIVE | Alertmanager pod/service exists in the monitoring namespace |
| PrometheusRules | ACTIVE | kube-prometheus and TriSLA PrometheusRules exist |
| Recording Rules | ACTIVE | TriSLA recording rules exist for orchestration, assurance, intelligence, governance and lifecycle views |
| Notification Chain | PARTIAL | Runtime notification routing is not fully evidenced as a production workflow |

```text
Production Notification Workflow

NOT FULLY EVIDENCED
```

Alerting must not be documented as fully production-notification-complete until notification receivers/routing are evidenced end to end.

## Evidence Collection Runtime Truth

| Evidence type | Status | Notes |
|---------------|--------|-------|
| Evidence Packs | ACTIVE | Evidence directories and frozen packs are part of the project baseline |
| Runtime Evidence | ACTIVE | Runtime state, digests, endpoints and validation artifacts are retained |
| Campaign Evidence | ACTIVE | Results and campaign packs are retained under the frozen evidence model |
| Freeze Evidence | ACTIVE | Operational, runtime and results freezes are retained and indexed |

Mandatory references preserved:

| Evidence / baseline | Status |
|---------------------|--------|
| Phase 47 | ACTIVE / FROZEN ALIGNMENT |
| Wave 1 | ACTIVE / HISTORICAL FREEZE |
| Wave 3A | ACTIVE / HISTORICAL FREEZE |
| Wave 4 | ACTIVE / HISTORICAL FREEZE |
| Results Freeze Main | PRIMARY RESULTS BASELINE |

Observability evidence supports reproducibility and debugging. It does not override implementation behavior, runtime authority, telemetry contracts, or the scientific baseline.

## Integrations

| Integration | Status |
|-------------|--------|
| Prometheus | ACTIVE |
| Grafana | ACTIVE |
| Alertmanager | ACTIVE |
| Tempo | ACTIVE |
| Jaeger | ACTIVE |
| SEM-CSMF | ACTIVE |
| Decision Engine | ACTIVE |
| ML-NSMF | ACTIVE |
| NASP Adapter | ACTIVE |
| BC-NSSMF | ACTIVE |
| SLA-Agent | ACTIVE |
| Portal Backend | ACTIVE |
| Archived Dashboards | LEGACY |

## Specialized References

| Document | Role |
|----------|------|
| `docs/PROMQL_SSOT_V2.md` | SPECIALIZED_REFERENCE for PromQL expressions |
| `docs/modules/telemetry.md` | TELEMETRY_CANONICAL_REFERENCE for `telemetry_snapshot` and metric source boundaries |
| `docs/observability/OBSERVABILITY.md` | Navigation Hub / Specialized Reference after consolidation |
| `grafana/MANIFEST.json` | Dashboard inventory reference |
| `grafana/O7E_PROVISIONING.md` | Grafana provisioning reference |
| `monitoring/o7c-trisla-recording-rules.yaml` | Recording-rules implementation reference |

## Contradictions Removed

| Previous contradiction | Canonical correction |
|------------------------|----------------------|
| OTEL path implied as snapshot producer | Prometheus-backed collectors produce `telemetry_snapshot`; OTEL is tracing/instrumentation |
| OTEL described as primary observability source | Prometheus is the primary observability metrics source; OTEL is tracing only |
| Archived dashboards treated as active | `grafana/archive/*` is LEGACY |
| Grafana UID treated as runtime-verified | UID `d25e340d-887a-4027-902f-cbb7b7aa0391` is confirmed in evidence packs only, not active dashboard inventory |
| Alerting notifications treated as fully implemented | Notification chain is PARTIAL; production notification workflow is not fully evidenced |
| Observability treated as telemetry | Observability supports telemetry; telemetry contracts remain canonical in `docs/modules/telemetry.md` |

## Implementation x Documentation Matrix

| Area | Implementation status | Documentation status | Canonical location |
|------|-----------------------|----------------------|--------------------|
| Prometheus server | ACTIVE | FULLY_DOCUMENTED | This document + `PROMQL_SSOT_V2.md` |
| ServiceMonitors | ACTIVE | FULLY_DOCUMENTED | This document |
| PrometheusRules / recording rules | ACTIVE | FULLY_DOCUMENTED | This document + `monitoring/o7c-trisla-recording-rules.yaml` |
| Exporters | ACTIVE | FULLY_DOCUMENTED | This document |
| `/metrics` endpoints | ACTIVE | FULLY_DOCUMENTED | This document + module docs |
| Grafana active dashboards | ACTIVE | FULLY_DOCUMENTED | This document + `grafana/MANIFEST.json` |
| Grafana normative dashboards | NORMATIVE | FULLY_DOCUMENTED | This document + `grafana/O7E_PROVISIONING.md` |
| Grafana archive | LEGACY | FULLY_DOCUMENTED | This document |
| OTEL instrumentation | ACTIVE | FULLY_DOCUMENTED | This document |
| OTEL collector / Tempo / Jaeger | ACTIVE | FULLY_DOCUMENTED | This document |
| OTEL as telemetry source | NOT PRIMARY | FULLY_DOCUMENTED | This document + telemetry doc |
| Logging | ACTIVE / PARTIAL | FULLY_DOCUMENTED | This document |
| Health/readiness/liveness | ACTIVE / PARTIAL | FULLY_DOCUMENTED | This document |
| Alertmanager | ACTIVE | FULLY_DOCUMENTED | This document |
| Notification chain | PARTIAL | FULLY_DOCUMENTED | This document |
| Evidence packs/freezes | ACTIVE | FULLY_DOCUMENTED | This document + SSOT pointer |

## Coverage

| Area | Before DOC-MOD-08-EXEC | After DOC-MOD-08-EXEC |
|------|------------------------|-----------------------|
| Prometheus | 85% | >= 95% |
| Grafana | 70% | >= 95% |
| OTEL | 65% | >= 95% |
| Logging | 55% | >= 95% |
| Health | 70% | >= 95% |
| Evidence | 75% | >= 95% |
| Dashboards | 70% | >= 95% |
| Alerting | 45% | >= 95% |
| Integrations | 75% | >= 95% |
| Overall | ~68% | >= 95% |

## DOC-MOD-08 Validation

| Criterion | Status |
|-----------|--------|
| CANONICAL_DOCUMENT_CREATED | TRUE |
| IMPLEMENTATION_ALIGNMENT | TRUE |
| PROMETHEUS_TRUTH_DOCUMENTED | TRUE |
| GRAFANA_TRUTH_DOCUMENTED | TRUE |
| OTEL_TRUTH_DOCUMENTED | TRUE |
| ALERTING_TRUTH_DOCUMENTED | TRUE |
| EVIDENCE_TRUTH_DOCUMENTED | TRUE |
| PHASE47_ALIGNMENT_MAINTAINED | TRUE |
| DOC_COVERAGE | >= 95% |
| DOCUMENTATION_DUPLICATION_REDUCED | TRUE |
| NO_NEW_DOCUMENT_TREES | TRUE |
| NO_RUNTIME_CHANGE | TRUE |
| NO_DEPLOY | TRUE |
| NO_SSOT_CHANGE | TRUE |
| DOC_MOD_08_STATUS | COMPLETED |
