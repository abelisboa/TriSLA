# Telemetry Layer

> **Operational entry point** for TriSLA multidomain telemetry.
> PromQL definitions are maintained with the active collectors and Helm monitoring resources.
> Implementation SSOT: `apps/portal-backend/src/telemetry/`, `apps/sla-agent-layer/src/revalidate/`, `apps/sem-csmf/src/decision_engine_client.py`, `apps/decision-engine/src/`, and `apps/nasp-adapter/src/metrics_collector.py`.


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

The Telemetry Layer is the **Multidomain Telemetry Collection and Distribution Layer**.

**Telemetry Layer does not make decisions.**
**Telemetry Layer does not execute admission.**
**Telemetry Layer does not execute blockchain.**

**Provides:**

- Telemetry Collection
- Telemetry Aggregation
- Telemetry Snapshot
- Telemetry Contracts
- Telemetry Explainability Inputs

**Does not provide:**

- Admission authority
- Blockchain registration
- Native NWDAF runtime
- Native 3GPP PM ingestion for unavailable metrics
- OTEL-derived telemetry snapshots

## Official Operational Chain

```text
UERANSIM
↓
RAN
↓
ONOS
↓
5GC
↓
Prometheus
↓
telemetry_snapshot
↓
SEM-CSMF
↓
Decision Engine
↓
ML-NSMF
↓
SLA-Agent
```

```text
Prometheus = PRIMARY TELEMETRY SOURCE
OTEL = OBSERVABILITY ONLY
```

Operational nuance: ONOS and some NASP/binding signals are conditional. The mandatory runtime source for `telemetry_snapshot` is Prometheus-backed collection and application collectors/proxies, not OTEL.

## telemetry_snapshot Runtime Truth

### Active Contract

```text
telemetry_snapshot
```

Structure:

```text
ran
transport
core
```

| Attribute | Runtime truth |
|-----------|---------------|
| Origin | Prometheus-backed collectors in Portal Backend and SLA-Agent; SEM may preserve/fetch PRB and compose payload for Decision Engine |
| Refresh | Collected during submit/revalidate/status paths; revalidate refreshes current telemetry via SLA-Agent |
| Consumers | SEM-CSMF, Decision Engine, ML-NSMF feature payload, SLA-Agent runtime assurance, Portal UI/status |
| Persistence | Embedded in response metadata, status/evidence payloads, and runtime evidence artifacts; no telemetry database |
| Primary object | `telemetry_snapshot`, not MDCE and not `telemetry_features` |

### Snapshot Window

The live Portal and SLA-Agent collectors query `[t-2s,t]` at a one-second step. Replay and shadow-specific snapshot policies are not part of the public runtime.

## Telemetry Contracts Runtime Truth

| Contract | Status | Runtime meaning |
|----------|--------|-----------------|
| `telemetry_snapshot` | ACTIVE | Primary runtime telemetry object |
| `telemetry_features` | CONDITIONAL | Built by SEM and consumed by Decision Engine only under conditional decision-score contexts; not the SLA-Agent runtime object |
| `domain_compliance` | ACTIVE | SLA-Agent compliance output by domain |
| `metric_explainability` | ACTIVE | Metric-level explanation rows used by Portal/XAI |
| `runtime_assurance` | ACTIVE | SLA-Agent assurance state and evidence |

## RAN Telemetry

| Metric | Status | Source / note |
|--------|--------|---------------|
| PRB | ACTIVE / PROXY | `trisla_ran_prb_utilization` via `trisla-ran-ue-upf-proxy` |
| UE Count | DERIVED | NASP/MDCE or kube-derived count, not native RAN PM |
| RAN latency | PROXY | `trisla_ran_latency_ms` or simulator/proxy source when present |
| RAN reliability | PROXY | Derived as transport delivery reliability proxy, generally `100 - packet_loss_pct` |
| RSRP | NOT_AVAILABLE | No active runtime source in the frozen implementation |
| RSRQ | NOT_AVAILABLE | No active runtime source in the frozen implementation |
| SINR | NOT_AVAILABLE | No active runtime source in the frozen implementation |
| QoS PM | NOT_AVAILABLE | No active native QoS PM collector in the frozen implementation |

## Transport Telemetry

| Metric | Status | Source / note |
|--------|--------|---------------|
| RTT | ACTIVE | `probe_duration_seconds` blackbox probe, converted to ms |
| Latency | DERIVED | Operational alias over RTT/latency fields |
| Jitter | DERIVED | Probe spread/window over `probe_duration_seconds` |
| Packet Loss | DERIVED | Container network packet drop ratio in the data-plane namespace |
| Bandwidth | PROXY | `trisla_ran_ue_proxy_throughput_bps` converted to Mbps |
| Topology Status | CONDITIONAL | ONOS/O5C transport binding path |
| Link Status | CONDITIONAL | ONOS/O5C transport binding path |

Bandwidth is not measured as a native transport-capacity PM on the hot path; it is a proxy throughput signal.

## Core Telemetry

| Metric | Status | Source / note |
|--------|--------|---------------|
| CPU | ACTIVE | Prometheus process/container aggregate, with env override support |
| Memory | ACTIVE | Prometheus process/container aggregate, with env override support |
| Availability | PROXY | Probe success plus Kubernetes deployment availability proxy |
| Reliability | PROXY | Operational proxy, not native 3GPP reliability PM |
| AMF Health | CONDITIONAL | Binding/probe context when available |
| SMF Health | CONDITIONAL | Binding/probe context when available |
| UPF Health | CONDITIONAL | Binding/probe context when available |
| Native 3GPP PM | NOT_AVAILABLE | No active native 3GPP PM ingestion in the frozen runtime |
| Session PM | NOT_AVAILABLE | No active session PM collector in the hot path |
| Attach PM | NOT_AVAILABLE | No active attach PM collector in the hot path |

## Prometheus Runtime Truth

| Query key | Status | Runtime source |
|-----------|--------|----------------|
| `RAN_PRB` | ACTIVE | `trisla_ran_prb_utilization{job="trisla-ran-ue-upf-proxy"}` |
| `TRANSPORT_RTT` | ACTIVE | `probe_duration_seconds` blackbox probe |
| `CORE_CPU` | ACTIVE | Env-overridable CPU aggregate |
| `CORE_MEMORY` | ACTIVE | Env-overridable memory aggregate |
| `TRANSPORT_PACKET_LOSS` / `TRANSPORT_PACKET_LOSS_PCT` | ACTIVE | Container packet drop ratio |
| `CORE_AVAILABILITY` / `CORE_AVAILABILITY_PCT` | ACTIVE | Probe + kube deployment availability proxy |

Exporters and sources:

| Exporter / source | Status |
|-------------------|--------|
| node-exporter | ACTIVE |
| kube-state-metrics | ACTIVE |
| blackbox-exporter | ACTIVE |
| trisla-ran-ue-upf-proxy | ACTIVE |
| NASP metrics | CONDITIONAL / SUPPORTING |
| service metrics | ACTIVE |
| trisla-prb-simulator | LAB / FALLBACK ONLY |

This document is the operational telemetry entry point for the public release.

## OTEL Runtime Truth

Classification:

```text
PARTIAL
```

| Capability | Status | Notes |
|------------|--------|-------|
| Tracing | ACTIVE | FastAPI instrumentation and OTLP exporters appear across services |
| Instrumentation | ACTIVE | Service-level spans and HTTP metrics wrappers exist |
| Snapshot source role | NOT PRIMARY | OTEL remains observability-only; snapshots come from Prometheus-backed collectors |
| Metrics/logs completeness | PARTIAL | Environment-dependent and not the snapshot SSOT |

## MDCE Runtime Truth

| Context | Status | Notes |
|---------|--------|-------|
| NASP Capacity Context | ACTIVE | `/api/v1/metrics/multidomain`, capacity accounting, reservation ledger |
| Decision Engine Admission | NOT HOT PATH | `mdce.py` exists but is not wired into the canonical `/evaluate` ingress |
| SLA-Agent Revalidate | NOT HOT PATH | SLA-Agent revalidate uses `telemetry_snapshot`, not MDCE |

```text
MDCE != telemetry_snapshot
```

MDCE is a NASP/capacity and multidomain schema context. It must not be documented as the primary telemetry source for admission or SLA-Agent reassessment.

## NWDAF Runtime Truth

Classification:

```text
CONCEPT_ONLY
DOC_ONLY
```

```text
NO RUNTIME MODULE
NO NWDAF SERVICE
NO NWDAF API
```

NWDAF-like language may appear in historical or scientific documentation, but the frozen implementation does not include an operational NWDAF module, service, or API.

## Integrations

| Integration | Status |
|-------------|--------|
| Prometheus | ACTIVE |
| SEM-CSMF | ACTIVE |
| Decision Engine | ACTIVE |
| ML-NSMF | ACTIVE |
| SLA-Agent | ACTIVE |
| NASP Adapter | CONDITIONAL |
| MDCE | NOT HOT PATH |
| NWDAF | DOC ONLY |
| OTEL | OBSERVABILITY ONLY / PARTIAL |

## Persistence

| Item | Status | Mechanism |
|------|--------|-----------|
| `telemetry_snapshot` | ACTIVE | Response/status metadata and evidence payloads |
| runtime evidence | ACTIVE | Runtime freeze/evidence artifacts and status payloads |
| compliance evidence | ACTIVE | SLA-Agent compliance/explainability outputs |
| telemetry database | NOT IMPLEMENTED | No dedicated telemetry DB |

```text
NO TELEMETRY DATABASE
```

## Contradictions Removed

| Old claim | Correct runtime truth |
|-----------|-----------------------|
| Snapshot source corrected | Prometheus-backed collectors are canonical |
| NWDAF runtime scope corrected | DOC_ONLY / CONCEPT_ONLY |
| MDCE runtime scope corrected | NASP capacity context |
| Radio-quality native PM scope corrected | RSRP, RSRQ, and SINR are NOT_AVAILABLE |
| Native 3GPP PM scope corrected | NOT_AVAILABLE |
| ML feature-object scope corrected | Conditional contract only |
| Bandwidth scope corrected | PROXY |

## Implementation x Documentation Matrix

| Runtime item | Implementation status | Documentation status |
|--------------|-----------------------|----------------------|
| Prometheus-backed collection | ACTIVE | CANONICAL |
| `telemetry_snapshot` | ACTIVE | CANONICAL |
| `telemetry_features` | CONDITIONAL | CANONICAL |
| `domain_compliance` | ACTIVE | CANONICAL |
| `metric_explainability` | ACTIVE | CANONICAL |
| `runtime_assurance` | ACTIVE | CANONICAL |
| RAN PRB | ACTIVE / PROXY | CANONICAL |
| RSRP / RSRQ / SINR | NOT_AVAILABLE | CANONICAL |
| Transport RTT/jitter/packet loss | ACTIVE / DERIVED | CANONICAL |
| Bandwidth | PROXY | CANONICAL |
| Core CPU/memory | ACTIVE | CANONICAL |
| Core availability/reliability | PROXY | CANONICAL |
| MDCE | NASP capacity context / NOT HOT PATH | CANONICAL |
| NWDAF | DOC_ONLY | CANONICAL |
| OTEL | PARTIAL / OBSERVABILITY ONLY | CANONICAL |

## DOC-MOD-07 Validation

| Criterion | Value |
|-----------|-------|
| CANONICAL_DOCUMENT_CREATED | TRUE |
| IMPLEMENTATION_ALIGNMENT | TRUE |
| TELEMETRY_TRUTH_DOCUMENTED | TRUE |
| PROMETHEUS_TRUTH_DOCUMENTED | TRUE |
| OTEL_TRUTH_DOCUMENTED | TRUE |
| MDCE_TRUTH_DOCUMENTED | TRUE |
| NWDAF_TRUTH_DOCUMENTED | TRUE |
| PHASE47_ALIGNMENT_MAINTAINED | TRUE |
| DOC_COVERAGE | >= 95% |
| DOCUMENTATION_DUPLICATION_REDUCED | TRUE |
| NO_NEW_DOCUMENT_TREES | TRUE |
| NO_RUNTIME_CHANGE | TRUE |
| NO_DEPLOY | TRUE |
| NO_SSOT_CHANGE | TRUE |
| DOC_MOD_07_STATUS | COMPLETED |

## Canonical Observability Reference

Canonical observability reference: docs/modules/observability.md defines Prometheus/Grafana/OTEL/Alertmanager/health/evidence boundaries; telemetry_snapshot remains defined here.


## Public Release Packaging

The active telemetry proxy implementation is packaged at `apps/ran-ue-upf-proxy/` and has opt-in Helm resources under `helm/trisla/templates/`. It is disabled by default. Operators must supply an immutable image digest and environment-specific RAN, UE, and UPF endpoints before enabling `ranUeUpfProxy.enabled`. The PRB simulator is retained only as an explicit lab fallback and is not the production source.
