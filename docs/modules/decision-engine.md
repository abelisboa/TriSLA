# Decision Engine

## Runtime Position In TriSLA Flow

Runtime position and cross-module flow ordering are defined by [`docs/modules/interfaces.md`](interfaces.md). This module document does not duplicate the full chain.

Canonical interface reference: [docs/modules/interfaces.md](interfaces.md).


## Canonical Governance Reference

Decision Engine owns admission-decision evidence. Cross-module flow and evidence boundaries are documented in [`docs/modules/interfaces.md`](interfaces.md).

Telemetry canonical reference: [docs/modules/telemetry.md](telemetry.md). Admission telemetry arrives through ; Decision Engine does not query Prometheus on the  hot path.

> **Operational entry point** for the TriSLA Decision Engine (SLA admission control).
> Deep dives: [`docs/decision-engine/`](../decision-engine/README.md) (interfaces).
> Implementation SSOT: `apps/decision-engine/`. Digest SSOT: `baseline-registry/OPERATIONAL_BASELINE_REGISTRY.json`.

## Role (frozen architecture)

The Decision Engine is the **SLA admission authority**. It receives structured intent input from SEM-CSMF via I-01 HTTP, calls ML-NSMF for risk prediction, applies policy-governed admission rules, and returns a deterministic decision (`AC`, `RENEG`, or `REJ`).

**Does:**

- Evaluate SLA viability on `POST /evaluate` (sole admission ingress)
- Call ML-NSMF `POST /api/v1/predict` during each evaluation
- Apply hard PRB gates, multi-domain scoring, and slice-aware risk thresholds
- Build explainability artifacts (`xai_bundle`, snapshot, system XAI, decision evidence)
- Echo inbound metadata and NEST for traceability (Wave 1 / Wave 3A)

**Does not:**

- Interpret natural-language intent (SEM-CSMF)
- Train or host ML models (ML-NSMF)
- Orchestrate NASP slice creation (Portal → NASP Adapter, post-ACCEPT)
- Register on-chain (Portal → BC-NSSMF)
- Query Prometheus on the production `/evaluate` hot path (telemetry arrives via SEM in `telemetry_snapshot`)

Position in the frozen chain:

```text
Portal Backend → SEM-CSMF → Decision Engine (I-01 HTTP /evaluate)
                         ↘ ML-NSMF ← called by Decision Engine
Portal → NASP Adapter (orchestration) → BC-NSSMF → SLA-Agent → Portal
```

## Operational baseline (Phase 47)

| Item | Value |
|------|-------|
| Deployment | `trisla-decision-engine` |
| Image | `ghcr.io/abelisboa/trisla-decision-engine` |
| Operational digest | `sha256:9c31b9c5ca239f8a2b7dea6aab03dd528836696387fe906b9848697a310b6409` |
| Rollback digest (Wave 3A) | `sha256:fe26baf0150554a330bdc0e637f9ab7dc1b9e665b42c38f84e17eed2b8fd3733` |
| HTTP port | `8082` (cluster: `http://trisla-decision-engine:8082`) |
| gRPC port | `50051` — **TRACEABILITY_ONLY** (not production SSOT) |
| App version | `3.10.0` (`apps/decision-engine/src/main.py`) |
| Wave 1 | G3-A metadata echo — `TRACEABILITY_ONLY` |
| Wave 3A | G3-C NEST transmission — `TRACEABILITY_ONLY`; NEST consumption **NOT WIRED** |

Source: `baseline-registry/OPERATIONAL_BASELINE_REGISTRY.json` (Wave 3A operational freeze).

## Runtime

| Property | Value |
|----------|-------|
| Framework | FastAPI |
| Version | `3.10.0` |
| HTTP | `:8082` |
| gRPC | `:50051` — **TRACEABILITY_ONLY** (daemon thread; uses legacy `RuleEngine`, not production admission path) |
| Primary caller | SEM-CSMF (`apps/sem-csmf/src/decision_engine_client.py`) |

## REST API catalog

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness — module, Kafka status, gRPC thread |
| GET | `/metrics` | Prometheus scrape |
| **POST** | **`/evaluate`** | **SOLE ADMISSION INGRESS** — `SLAEvaluateInput` → `DecisionResult` |

**Not implemented on this service:** `POST /api/v1/evaluate`, `POST /api/v1/sla/submit` (Portal Backend).

## Production hot path

```text
POST /evaluate (SLAEvaluateInput)
  → merge telemetry_snapshot into context
  → resolve_nest_for_evaluate (minimal NestSubset from nest_id; inbound nest body ignored for rules)
  → DecisionService.process_decision_from_input
       → MLClient.predict_viability → POST {ML_NSMF}/api/v1/predict
       → engine._apply_decision_rules
       → (ACCEPT + BC_ENABLED) bc_client.register_sla_on_chain
       → build_decision_snapshot + explain_decision + persist_decision_evidence
       → attach_decision_evidence_metadata
  → echo_inbound_metadata (Wave 1 G3-A)
  → echo_inbound_nest (Wave 3A G3-C)
  → return DecisionResult
```

Detailed I-01 field contract: [`docs/decision-engine/interfaces/interfaces.md`](../decision-engine/interfaces/interfaces.md).

## I-01 contract — consume vs echo

| Field | Required | Consumed by rules | Runtime classification |
|-------|----------|-------------------|------------------------|
| `intent_id` | Yes | Yes | **ACTIVE** — correlation |
| `intent` | Yes | Yes | **ACTIVE** — coerced to `SLAIntent` |
| `nest_id` | No | Yes | **ACTIVE** — minimal `NestSubset` via `resolve_nest_for_evaluate` |
| `nest` | No | **No** | **TRACEABILITY_ONLY** — returned as `metadata.inbound_nest` (Wave 3A) |
| `context` | No | Yes | **ACTIVE** — duration, optional features |
| `context.telemetry_features` | No | Conditional | **ACTIVE** only when `DECISION_SCORE_MODE=true` |
| `telemetry_snapshot` | No | Yes | **ACTIVE** — PRB, RTT, CPU, MEM for rules + ML payload |
| `metadata` | No | **No** | **TRACEABILITY_ONLY** — returned as `metadata.inbound_metadata` (Wave 1 G3-A) |

**Governance rule:** root `metadata` MUST NOT be copied into `SLAIntent.metadata` or passed to `_apply_decision_rules`.

## Admission logic SSOT

Implementation: `apps/decision-engine/src/engine.py` → `_apply_decision_rules`.  
Slice thresholds: `apps/decision-engine/src/decision_thresholds.py`.

### Decision outcomes

| Code | Label |
|------|-------|
| `AC` | ACCEPT |
| `RENEG` | RENEGOTIATE |
| `REJ` | REJECT |

### Hard PRB gates (first precedence)

Applied when `telemetry_snapshot.ran.prb_utilization` is present. Values > 1 are treated as percent and normalized to [0, 1].

| Env var | Default | Effect |
|---------|---------|--------|
| `HARD_PRB_REJECT` / `HARD_PRB_REJECT_THRESHOLD` | `95` (→ 0.95) | Immediate **REJECT** |
| `HARD_PRB_RENEGOTIATE` / `HARD_PRB_RENEGOTIATE_THRESHOLD` | `85` (→ 0.85) | Immediate **RENEG** |

### Multi-domain weights

After hard PRB gates, domain scores compose `final_score`:

| Domain | Weight | Inputs (from `telemetry_snapshot`) |
|--------|--------|-------------------------------------|
| RAN | **0.70** | `ran.prb_utilization` → `ran_score = 1 - prb_normalized` |
| Transport | **0.20** | `transport.latency_ms` / `rtt`, `jitter_ms` |
| Core | **0.10** | `core.cpu_utilization`, `core.memory_utilization` (core score capped at 0.3) |

```text
final_score = 0.70 × ran_score + 0.20 × transport_score + 0.10 × core_score
final_risk = 1 - final_score
```

### Final score thresholds

| Env var | Default | Effect on threshold path |
|---------|---------|--------------------------|
| `FINAL_SCORE_ACCEPT_THRESHOLD` | `0.70` | `final_score ≥` → ACCEPT |
| `FINAL_SCORE_RENEGOTIATE_THRESHOLD` | `0.45` | `final_score ≥` → RENEG; below → REJECT |

### Slice risk thresholds (`decision_thresholds.py`)

Applied to `final_risk` under policy-governed mode (`risk < accept` → ACCEPT path via policy logic; `accept ≤ risk < renegotiate` → RENEG; `risk ≥ renegotiate` → REJECT).

| Slice | accept | renegotiate |
|-------|--------|-------------|
| URLLC | 0.48 | 0.72 |
| eMBB | 0.56 | 0.78 |
| mMTC | 0.54 | 0.76 |

Default fallback (unknown slice): accept `0.55`, renegotiate `0.75`.

### Policy-governed mode (operational default)

| Env var | Default | Behavior |
|---------|---------|----------|
| `POLICY_GOVERNED_MODE` | `true` | Precedence: hard PRB → slice risk thresholds → ML classifier refinement → fallback ACCEPT |
| `ML_REFINEMENT_CONFIDENCE` | `0.6` | Minimum classifier confidence for ML refinement |
| `ML_CAN_OVERRIDE_REJECT` | `false` | When false, ML REJECT class maps to safe RENEG |
| `PRB_RISK_ALPHA` | `0.15` | Documented in XAI bundle metadata |

When `POLICY_GOVERNED_MODE=false`, legacy classifier vs threshold-fallback path applies.

### Decision score mode (alternate path)

| Env var | Default | Behavior |
|---------|---------|----------|
| `DECISION_SCORE_MODE` | `false` | When `true`, delegates to `decision_score_mode.score_mode_decide` (continuous multi-objective score) |

Uses `context.telemetry_features` and optional feasibility inputs. **Not the default production path** at Wave 3A freeze digest.

## Explainability pipeline

All stages run in `DecisionService.process_decision_from_input` after rules (S30 path). Outputs are attached to `DecisionResult.metadata` unless noted.

| Stage | Source | Purpose | Key exposed fields |
|-------|--------|---------|-------------------|
| **xai_bundle** | `engine._apply_decision_rules` | Internal decision trace | `decision_mode`, `threshold_decision`, `final_decision`, `decision_source`, `top_factors`, `dominant_domain`, `decision_explanation_plain`, `hard_prb_thresholds`, domain scores |
| **decision_snapshot** | `decision_snapshot.build_decision_snapshot` | Deterministic decision record | Domain metrics, `sla_compliance`, bottleneck hints → `metadata.decision_snapshot` |
| **system_xai** | `system_xai.explain_decision` | System-aware WHY (physical domains) | `cause`, `explanation`, `system_aware` → `metadata.system_xai_explanation` |
| **decision_evidence** | `decision_evidence.attach_decision_evidence_metadata` | Quantitative metric rows | `metric`, `observed`, `threshold`, `delta`, `rule` → `metadata.decision_evidence[]` |

**DecisionResult top-level mirrors** (from xai_bundle, no rule change): `decision_mode`, `threshold_decision`, `final_decision`, `confidence_score`, `predicted_decision_class`.

WHY-style content for Portal/consumers: combine `reasoning`, `metadata.decision_explanation_plain`, `metadata.system_xai_explanation`, and `metadata.decision_evidence`.

## Governance runtime truth

Modules `orchestration_authority.py` and `lifecycle_authority.py` exist in the codebase and define FASE 3/4 metadata shapes (`orchestration_required`, `lifecycle_event`, `governance_event`, etc.).

| Module | Code status | Hot path (`POST /evaluate`) |
|--------|-------------|----------------------------|
| `orchestration_authority.py` | **IMPLEMENTED** | **NOT WIRED** — `enrich_orchestration_authority_metadata` has zero production callers |
| `lifecycle_authority.py` | **IMPLEMENTED** | **NOT WIRED** — `enrich_lifecycle_governance_metadata` called in tests only |

**Runtime at digest `9c31b9c5…`:** these authority enrichers do **not** run on `/evaluate`. Portal Backend uses **legacy fallback** when authority fields are absent:

- Orchestration: `decision == ACCEPT` triggers NASP instantiate (`apps/portal-backend/src/services/nasp.py`)
- Lifecycle/governance: Portal legacy composer (`apps/portal-backend/src/routers/sla.py`)

Do **not** document FASE 3/4 authority emission as active runtime behavior until wired in `service.py`.

Target contract reference (aspirational): `docs/TRISLA_E2E_FLOW_CANONICAL.md` FASE 3/4 metadata table.

## Integrations

| Integration | Runtime status | Notes |
|-------------|----------------|-------|
| SEM-CSMF | **ACTIVE** | Inbound I-01 HTTP; SEM pushes payload, receives `DecisionResult` |
| ML-NSMF | **ACTIVE** | `POST /api/v1/predict` on every `/evaluate` |
| BC-NSSMF | **CONDITIONAL** | `BC_ENABLED=false` default → stub; `register_sla_on_chain` on ACCEPT when enabled |
| NASP Adapter | **CLIENT EXISTS / NOT HOT PATH** | `NASPAdapterClient` instantiated in `main.py`; never invoked on `/evaluate` |
| Portal Backend | **CLIENT EXISTS / NOT HOT PATH** | `PortalBackendClient` instantiated; never invoked on `/evaluate` |
| Kafka | **CONDITIONAL / NOT HOT PATH** | `KAFKA_ENABLED=false`; producer/consumer offline unless explicitly enabled |
| Prometheus ResourceEvaluator | **ALTERNATE PATH** | Used in `engine.decide()` (SEM-fetch path), **not** in `/evaluate` hot path |
| MDCE | **NOT WIRED** | `mdce.py` not imported in production ingress |

## Observability

| Layer | Implementation |
|-------|----------------|
| **Prometheus** | `trisla_http_requests_total`, `trisla_http_request_duration_seconds`; `GET /metrics` |
| **OTEL** | `OTLP_ENABLED`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTLP_ENDPOINT_GRPC`; FastAPI instrumentation |
| **Tracing spans** | `evaluate_sla`, `service_process_decision_from_input`, `predict_viability_ml`, `decision_engine_decide` (alternate path) |
| **Log markers** | `[PRB RECEIVED]`, `[MULTI-DOMAIN SCORE]`, `[HYBRID DECISION]`, `[ENGINE] policy_governed`, `[S30]` |

Telemetry for admission decisions comes from **`telemetry_snapshot`** supplied by SEM-CSMF on I-01, not from direct Prometheus queries on the hot path.

## Persistence

| Store | Mechanism | Notes |
|-------|-----------|-------|
| **Evidence snapshots** | File JSON under `$TRISLA_EVIDENCE_DIR/21_decision_engine_snapshots/` | Default dir `/tmp/trisla_evidence`; `decision_{intent_id}.json`, `explanation_{intent_id}.json` |
| **decisions_storage** | In-memory dict in `main.py` | Ephemeral per pod; not durable |
| **SQL / ORM** | **None** | No database in this module |

Env: `TRISLA_EVIDENCE_DIR`.

## Legacy and non-hot paths

| Component | Status |
|---------|--------|
| `RuleEngine` / `DecisionMaker` | **LEGACY** — gRPC and Kafka consumer only |
| gRPC I-01 (`SendNESTMetadata`) | **TRACEABILITY_ONLY** |
| Kafka Consumer | **CONDITIONAL / NOT HOT PATH** (`KAFKA_ENABLED=false`) |
| Kafka Producer | **CONDITIONAL / NOT HOT PATH** |
| MDCE evaluation (`mdce.py`) | **NOT WIRED** |
| `orchestration_authority` | **NOT WIRED** |
| `lifecycle_authority` | **NOT WIRED** |
| `interfaces/hooks.py` (RAN/TN/CN shadow) | **NOT WIRED** (`INTERFACE_LAYER_ENABLED=false` default) |
| `engine.decide()` SEM-fetch path | **ALTERNATE** — not used when SEM sends full payload via HTTP |
| `DECISION_SCORE_MODE` | **ALTERNATE** — off by default |

## Key environment variables

| Variable | Default | Role |
|----------|---------|------|
| `ML_NSMF_HTTP_URL` | `http://127.0.0.1:8081` | ML predict endpoint |
| `BC_ENABLED` | `false` | Blockchain registration |
| `TRISLA_PRIVATE_KEY` | none | Required external signing key when blockchain registration is enabled |
| `KAFKA_ENABLED` | `false` | Async decision events |
| `POLICY_GOVERNED_MODE` | `true` | Operational admission mode |
| `DECISION_SCORE_MODE` | `false` | Alternate score-based admission |
| `HARD_PRB_REJECT` | `95` | Hard reject gate |
| `HARD_PRB_RENEGOTIATE` | `85` | Hard renegotiate gate |
| `FINAL_SCORE_ACCEPT_THRESHOLD` | `0.70` | Multi-domain accept |
| `FINAL_SCORE_RENEGOTIATE_THRESHOLD` | `0.45` | Multi-domain renegotiate |
| `TRISLA_EVIDENCE_DIR` | `/tmp/trisla_evidence` | Snapshot persistence |
| `HTTP_PORT` | `8082` | Service port |
| `GRPC_PORT` | `50051` | Legacy gRPC thread |

## Related documentation

| Topic | Location |
|-------|----------|
| I-01 field SSOT | [`docs/decision-engine/interfaces/interfaces.md`](../decision-engine/interfaces/interfaces.md) |
| I-01 schema registry | `interface-registry/i01/I01_SCHEMA_REGISTRY.json` |
| Wave 3A freeze | `baseline-registry/WAVE3A_OPERATIONAL_FREEZE.md` |

## Canonical Telemetry Reference

Canonical telemetry reference: docs/modules/telemetry.md defines telemetry_snapshot origin, freshness, metric classes, and the Prometheus primary-source boundary used by the Decision Engine.

## Canonical Observability Reference

Canonical observability reference: docs/modules/observability.md defines Decision Engine metrics, OTEL tracing, health, dashboards, and alerting boundaries.
