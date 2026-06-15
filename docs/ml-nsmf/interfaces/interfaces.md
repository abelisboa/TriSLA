# ML-NSMF Interfaces

> Specialized reference. Canonical cross-module interface truth: [`docs/modules/interfaces.md`](../../modules/interfaces.md).

> **Operational entry point:** [`docs/modules/ml-nsmf.md`](../../modules/ml-nsmf.md)

## Primary — HTTP I-05 (Production SSOT)

| Property | Value |
|----------|-------|
| Direction | Decision Engine → ML-NSMF |
| Transport | HTTP |
| Method | `POST` |
| Path | `/api/v1/predict` |
| Port | `8081` |
| Classification | **SOLE INFERENCE INGRESS** |
| Client | `apps/decision-engine/src/ml_client.py` |
| Server | `apps/ml-nsmf/src/main.py` → `DualLoadService.predict` |

### Request

JSON feature dict (see canonical doc § Request contract). Built by DE from SLA intent + context. Some telemetry fields are **sent but not consumed** by ML feature builder.

### Response

```json
{
  "latency_ms": <float>,
  "prediction": { "risk_score", "viability_score", "slice_adjusted_risk_score", ... },
  "explanation": { "method", "features_importance", "reasoning", "top_factors", ... }
}
```

ML-NSMF **does not** return final SLA decisions. DE maps scores to ACCEPT / RENEG / REJECT.

---

## Conditional — Kafka Producer (I-03 legacy async)

| Property | Value |
|----------|-------|
| Direction | ML-NSMF → (optional) async consumers |
| Topic | `trisla-ml-predictions` |
| Runtime | **CONDITIONAL** — `KAFKA_ENABLED=false` by default |
| Hot path | **NO** — HTTP response is authoritative; producer is fire-and-forget side effect after predict |

Also defined (not called from `/predict` hot path): `trisla-ml-xai` via `send_xai_explanation`.

---

## Not production SSOT

| Path | Status |
|------|--------|
| SEM-CSMF → Kafka → ML-NSMF | **OBSOLETE** — SEM does not push to ML via Kafka in production; DE calls HTTP |
| Kafka consumer `nasp-metrics` | **CONDITIONAL / NOT HOT PATH** — `MetricsConsumer` not invoked on predict |
| Direct Portal / SEM → ML | **NOT IMPLEMENTED** on admission path |

---

## Integration summary (frozen)

```text
Decision Engine POST /evaluate
    → POST /api/v1/predict (ML-NSMF)
    → HTTP response
    → Decision Engine admission rules
```
