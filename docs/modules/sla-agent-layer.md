# SLA-Agent Layer

## Runtime Position In TriSLA Flow

Runtime position and cross-module flow ordering are defined by [`docs/modules/interfaces.md`](interfaces.md). This module document does not duplicate the full chain.

Canonical interface reference: [docs/modules/interfaces.md](interfaces.md).

Telemetry canonical reference: [docs/modules/telemetry.md](telemetry.md). SLA-Agent consumes  for reassessment and runtime assurance.

> **Operational entry point** for TriSLA temporal reassessment and runtime assurance.
> Deep dives: [`docs/sla-agent/`](../sla-agent/README.md) (interfaces, research model, minimal architecture pointer).
> Implementation SSOT: `apps/sla-agent-layer/`. Digest SSOT: `baseline-registry/OPERATIONAL_BASELINE_REGISTRY.json`.

## Frozen status

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

## Role (frozen architecture)

The SLA-Agent is the **Temporal Reassessment and Runtime Assurance Authority**.

**SLA-Agent does not decide admission.**
**SLA-Agent does not execute blockchain.**
**SLA-Agent does not compose governance metadata.**

**Does:**

- Telemetry Reassessment
- Compliance Evaluation
- Explainability Generation
- Runtime Assurance

**Does not:**

- Make ACCEPT / RENEGOTIATE / REJECT admission decisions
- Register transactions or persist blockchain evidence
- Compose governance metadata for SEM or Portal
- Treat Kafka as the primary production ingress
- Treat domain agents or federated policies as the hot path

Position in the frozen chain:

```text
Portal Backend -> SEM-CSMF -> Decision Engine -> Portal Backend
Portal Backend -> NASP Adapter -> BC-NSSMF -> SLA-Agent -> Portal Backend
Portal Backend -> SLA-Agent revalidate -> Prometheus Collector -> Runtime Assurance -> Portal Backend
```

## Operational baseline (Phase 47)

| Item | Value |
|------|-------|
| Deployment | `trisla-sla-agent-layer` |
| Operational digest | `sha256:ca46e4a84d6ade3917d9d559ad2fe3ba7fa5269cbf27d2d0ad7c473ba104d371` |
| HTTP port | `8084` |
| App version | `3.11.0` |
| Primary caller | Portal Backend |
| Runtime responsibility | Temporal reassessment and runtime assurance |

## REST API catalog

### Active

| Method | Path | Classification | Purpose |
|--------|------|----------------|---------|
| GET | `/health` | ACTIVE | Liveness and domain-agent health summary |
| GET | `/metrics` | ACTIVE | Prometheus scrape for HTTP/runtime metrics |
| POST | `/api/v1/agent/revalidate-telemetry` | ACTIVE / SOLE REVALIDATE AUTHORITY | Portal delegated telemetry reassessment |
| POST | `/api/v1/runtime-assurance/evaluate` | ACTIVE | On-demand runtime assurance evaluation |

### Conditional

| Method | Path | Classification | Activation condition |
|--------|------|----------------|----------------------|
| POST | `/api/v1/ingest/pipeline-event` | CONDITIONAL | Active only when ACCEPT + ORCHESTRATION SUCCESS + BC COMMITTED |

### Conditional domain agents

| Method | Path | Classification |
|--------|------|----------------|
| POST | `/api/v1/agents/ran/collect` | CONDITIONAL / NOT HOT PATH |
| POST | `/api/v1/agents/transport/collect` | CONDITIONAL / NOT HOT PATH |
| POST | `/api/v1/agents/core/collect` | CONDITIONAL / NOT HOT PATH |
| POST | `/api/v1/coordinate` | CONDITIONAL / NOT HOT PATH |
| GET | `/api/v1/slos` | CONDITIONAL / NOT HOT PATH |

### Actuation

| Path | Classification |
|------|----------------|
| `/api/v1/actuation/*` | CONDITIONAL / NOT WIRED |

Actuation endpoints persist audit and authorization state. They are not the normal runtime assurance path and must not be documented as automatic domain mutation.

### Research

| Method | Path | Classification |
|--------|------|----------------|
| POST | `/api/v1/s29/create-snapshot` | RESEARCH / NOT HOT PATH |
| POST | `/api/v1/s29/generate-explanation` | RESEARCH / NOT HOT PATH |

## Hot path

### Revalidate

Classification: **SOLE REVALIDATE AUTHORITY**

```text
Portal
    ↓
POST /sla/revalidate-telemetry
    ↓
SLA-Agent
POST /api/v1/agent/revalidate-telemetry
    ↓
Prometheus Collector
    ↓
Compliance
    ↓
Explainability
    ↓
Runtime Assurance
    ↓
Portal
```

Implementation anchor: `apps/sla-agent-layer/src/revalidate/handler.py` and `apps/sla-agent-layer/src/revalidate/collector.py`.

### Ingest

Classification: **CONDITIONAL**

```text
Portal
    ↓
ACCEPT
+
ORCHESTRATION SUCCESS
+
BC COMMITTED
    ↓
POST /api/v1/ingest/pipeline-event
    ↓
Runtime Assurance
    ↓
Portal
```

This path records closed-loop observation after successful admission, orchestration, and blockchain commit. It is not an admission path.

## Telemetry Runtime Truth

| Runtime object / concept | Status | Notes |
|--------------------------|--------|-------|
| `telemetry_snapshot` | ACTIVE | Runtime object consumed by reassessment and assurance |
| `telemetry_snapshot.ran` | ACTIVE | RAN metrics block |
| `telemetry_snapshot.transport` | ACTIVE | Transport metrics block |
| `telemetry_snapshot.core` | ACTIVE | Core metrics block |
| `collect_domain_metrics_async` | ACTIVE | Prometheus-backed collector in `revalidate/collector.py` |
| PromQL SSOT | ACTIVE | Runtime queries are sourced from `revalidate/promql_ssot.py` / Prometheus configuration |
| `telemetry_features` | NOT IMPLEMENTED | Not a runtime object for this module |
| MDCE | NOT IMPLEMENTED as runtime identifier | Dissertation concept, not code identifier on the SLA-Agent hot path |

Dissertation concepts do not automatically equal runtime identifiers. In this module, the operational telemetry object is `telemetry_snapshot`, not `telemetry_features` or MDCE.

## Domain Agents Runtime Truth

| Agent | Status |
|-------|--------|
| AgentRAN | CONDITIONAL |
| AgentTransport | CONDITIONAL |
| AgentCore | CONDITIONAL |

```text
Prometheus Collector = PRIMARY
Domain Agents = SECONDARY
```

Domain agents exist and can collect domain data through conditional endpoints, but the primary reassessment path uses the Prometheus collector.

## Compliance Runtime Truth

| Component | Status | Notes |
|-----------|--------|-------|
| `compute_metric_compliance` | ACTIVE | Per-metric compliance function |
| `compute_all_domains_compliance` | ACTIVE | Aggregates RAN, transport, and core compliance |
| `SLICE_THRESHOLDS.URLLC` | ACTIVE | Slice-specific threshold set |
| `SLICE_THRESHOLDS.EMBB` | ACTIVE | Slice-specific threshold set |
| `SLICE_THRESHOLDS.MMTC` | ACTIVE | Slice-specific threshold set |
| `domain_compliance` | ACTIVE | Runtime compliance block exposed per domain |

Implementation anchor: `apps/sla-agent-layer/src/domain_compliance.py`.

## Explainability Runtime Truth

`metric_explainability[]` is ACTIVE and carries metric-level explanation rows.

| Field | Status |
|-------|--------|
| `metric` | ACTIVE |
| `observed` | ACTIVE |
| `threshold` | ACTIVE |
| `compliance_score` | ACTIVE |
| `status` | ACTIVE |
| `source` | ACTIVE |

| Explainability output | Status |
|----------------------|--------|
| `measurement_semantics` | ACTIVE |
| `domain_explainability` | ACTIVE |

Implementation origin: Sprint 6C, Sprint 6D, and Sprint 6E. These additions expose already-computed domain compliance and measurement semantics without changing admission decisions.

## Runtime Assurance Runtime Truth

### Active fields

| Field | Status |
|-------|--------|
| `violations` | ACTIVE |
| `warnings` | ACTIVE |
| `drift_detected` | ACTIVE |
| `drift_indicators` | ACTIVE |
| `recommendation` | ACTIVE |
| `bottleneck_domain` | ACTIVE |
| `sla_compliance` | ACTIVE |
| `domain_compliance` | ACTIVE |

### Runtime states

| State | Status |
|-------|--------|
| `COMPLIANT` | ACTIVE |
| `WARNING` | ACTIVE |
| `AT_RISK` | ACTIVE |
| `VIOLATED` | ACTIVE |
| `INCOMPLETE` | NOT WIRED |

Implementation anchor: `apps/sla-agent-layer/src/runtime_slo_evaluator.py` and `apps/sla-agent-layer/src/runtime_assurance_store.py`.

## Governance Runtime Truth

**SLA-Agent does not generate governance.**

| Item | Runtime truth |
|------|---------------|
| `runtime_governance_event` | STATE TRANSITION EVENT |
| Blockchain meaning | NOT BLOCKCHAIN EVENT |
| `blockchain_scope` | `none` |

Runtime assurance may expose a state transition event for the Portal to observe. That event is not a blockchain event and must not be documented as on-chain governance.

## Integrations

| Integration | Status |
|-------------|--------|
| Portal Backend | ACTIVE |
| Prometheus | ACTIVE |
| NASP Adapter | CONDITIONAL |
| BC-NSSMF Gate | CONDITIONAL |
| ONOS TN002 | CONDITIONAL |
| Kafka Consumer | NOT STARTED |
| Decision Engine | NOT HOT PATH |
| Domain Agents | NOT HOT PATH |
| Federated Policies | NOT HOT PATH |
| OTEL | PARTIAL |

## Observability

| Capability | Status |
|------------|--------|
| HTTP Metrics | ACTIVE |
| Health | ACTIVE |
| Readiness | ACTIVE through health/runtime checks |
| OTEL | PARTIAL |
| Assurance Guard | NOT WIRED |

HTTP metrics are exposed through `/metrics`. OTEL instrumentation exists but is environment-dependent.

## Persistence

| Store | Status | Mechanism |
|-------|--------|-----------|
| `runtime_assurance_store` | ACTIVE | Lightweight local state store |
| `admission_throttle_store` | ACTIVE | Actuation gate/throttle store |
| `actuation_audit_store` | ACTIVE | Actuation audit records |

```text
NO SQL
NO ORM
NO DATABASE
```

## Legacy and non-hot paths

| Component | Status |
|-----------|--------|
| Kafka consumer | NOT STARTED as production ingress |
| Legacy Kafka-mediated SLA-Agent chain | REMOVED as primary documentation path |
| Domain agents as primary runtime | REMOVED; secondary only |
| Federated execution | NOT HOT PATH |
| `/api/v1/policies/federated` | CONDITIONAL / NOT HOT PATH |
| `/api/v1/agents/*/action` | CONDITIONAL / NOT HOT PATH |
| `INCOMPLETE` runtime state | NOT WIRED |
| MDCE runtime identifier | NOT IMPLEMENTED |
| `telemetry_features` runtime object | NOT IMPLEMENTED |

## Documentation alignment matrix

| Runtime item | Implementation status | Documentation status |
|--------------|-----------------------|----------------------|
| Revalidate endpoint | ACTIVE | CANONICAL |
| Runtime assurance endpoint | ACTIVE | CANONICAL |
| Pipeline ingest | CONDITIONAL | CANONICAL |
| Prometheus collector | PRIMARY | CANONICAL |
| Domain agents | CONDITIONAL / SECONDARY | CANONICAL |
| Compliance engine | ACTIVE | CANONICAL |
| Explainability rows | ACTIVE | CANONICAL |
| Runtime governance event | STATE TRANSITION EVENT | CANONICAL |
| Kafka consumer | NOT STARTED | CANONICAL |
| Actuation | CONDITIONAL / NOT WIRED | CANONICAL |
| Research S29 endpoints | RESEARCH / NOT HOT PATH | CANONICAL |

## DOC-MOD-06 validation

| Criterion | Value |
|-----------|-------|
| CANONICAL_DOCUMENT_UPDATED | TRUE |
| IMPLEMENTATION_ALIGNMENT | TRUE |
| TELEMETRY_TRUTH_DOCUMENTED | TRUE |
| COMPLIANCE_TRUTH_DOCUMENTED | TRUE |
| EXPLAINABILITY_TRUTH_DOCUMENTED | TRUE |
| ASSURANCE_TRUTH_DOCUMENTED | TRUE |
| PHASE47_DIGEST_DOCUMENTED | TRUE |
| DOC_COVERAGE | >= 90% |
| DOCUMENTATION_DUPLICATION_REDUCED | TRUE |
| NO_NEW_DOCUMENT_TREES | TRUE |
| NO_RUNTIME_CHANGE | TRUE |
| NO_DEPLOY | TRUE |
| NO_SSOT_CHANGE | TRUE |
| DOC_MOD_06_STATUS | COMPLETED |

## Canonical Telemetry Reference

Canonical telemetry reference: docs/modules/telemetry.md defines telemetry_snapshot refresh, live collector window, Prometheus source, and SLA revalidation telemetry boundaries.

## Canonical Observability Reference

Canonical observability reference: docs/modules/observability.md defines SLA-Agent metrics, OTEL tracing, health, dashboards, and alerting boundaries.
