# Decision Engine Interfaces

> Specialized reference. Canonical cross-module interface truth: [`docs/modules/interfaces.md`](../../modules/interfaces.md).

> **Operational entry point:** [`docs/modules/decision-engine.md`](../../modules/decision-engine.md)

## I-01 Ingress (Production SSOT)

| Property | Value |
|----------|-------|
| Transport | HTTP |
| Method | `POST` |
| Path | `/evaluate` |
| Port | `8082` |
| Classification | **SOLE ADMISSION INGRESS** |
| Model | `SLAEvaluateInput` (`apps/decision-engine/src/models.py`) |
| Caller | SEM-CSMF (`apps/sem-csmf/src/decision_engine_client.py`) |

### Input fields — consume vs echo

| Field | Required | Consumed by rules | Notes |
|-------|----------|-------------------|-------|
| `intent_id` | Yes | Yes | Top-level correlation |
| `intent` | Yes | Yes | Coerced to `SLAIntent` |
| `nest_id` | No | Yes | Minimal `NestSubset` via `resolve_nest_for_evaluate` |
| `nest` | No | **No (echo only)** | Wave 3A G3-C — echoed in `DecisionResult.metadata.inbound_nest`; body **not** used for rules |
| `context` | No | Yes | Duration, optional telemetry features |
| `context.telemetry_features` | No | Conditional | Used only when `DECISION_SCORE_MODE=true` |
| `telemetry_snapshot` | No | Yes | PRB / RTT / CPU / MEM — supplied by SEM; **not** fetched via Prometheus on hot path |
| `metadata` | No | **No (echo only)** | Wave 1 G3-A — echoed in `DecisionResult.metadata.inbound_metadata` |

**Governance:** Root `metadata` MUST NOT be copied into `SLAIntent.metadata` or passed to `_apply_decision_rules`.

### Legacy transport

gRPC `:50051` / `SendNESTMetadata` — **TRACEABILITY_ONLY**. Not production SSOT. Uses legacy `RuleEngine`, not `engine._apply_decision_rules`.

---

## Downstream call (DE → ML-NSMF)

| Property | Value |
|----------|-------|
| Interface | I-05 (HTTP) |
| Method | `POST` |
| Path | `/api/v1/predict` |
| Client | `apps/decision-engine/src/ml_client.py` |
| Runtime | **ACTIVE** on every `/evaluate` |

---

## Output

| Destination | Transport | Runtime |
|-------------|-----------|---------|
| SEM-CSMF | HTTP response (`DecisionResult`) | **ACTIVE** |
| BC-NSSMF | `bc_client.register_sla_on_chain` | **CONDITIONAL** (`BC_ENABLED`) |
| Kafka (`trisla-decision-events`) | Producer | **CONDITIONAL** (`KAFKA_ENABLED=false` default) |
| SLA-Agent | — | **Not direct** — Portal/BC path |

### Output metadata (hot path)

`DecisionResult.metadata` is enriched on `/evaluate` by:

- `engine.py` / `service.py` — XAI bundle fields, ML scores, domain scores
- `decision_snapshot.py` — `decision_snapshot`
- `system_xai.py` — `system_xai_explanation`
- `decision_evidence.py` — `decision_evidence[]`
- `i01_metadata_echo.py` — `inbound_metadata`
- `i01_nest_echo.py` — `inbound_nest`

**Not enriched on hot path** (modules exist, not wired):

- `orchestration_authority.py` — orchestration authority fields
- `lifecycle_authority.py` — `lifecycle_event`, `governance_event`

See [Governance runtime truth](../../modules/decision-engine.md#governance-runtime-truth) in the canonical module doc.
