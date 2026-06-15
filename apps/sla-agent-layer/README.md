# SLA-Agent Layer

**Operational reference:** [`docs/modules/sla-agent-layer.md`](../../docs/modules/sla-agent-layer.md)

This README is intentionally minimal. Runtime role, endpoint classification, telemetry truth, compliance, explainability, runtime assurance, governance boundaries, integrations, observability, and persistence are documented in the canonical module document.

## Runtime identity

SLA-Agent is the **Temporal Reassessment and Runtime Assurance Authority**.

It does not decide admission, execute blockchain, or compose governance metadata.

## Primary path

```text
Portal Backend
    -> POST /api/v1/agent/revalidate-telemetry
SLA-Agent
    -> Prometheus Collector
    -> Compliance
    -> Explainability
    -> Runtime Assurance
    -> Portal Backend
```

## Baseline

| Item | Value |
|------|-------|
| Deployment | `trisla-sla-agent-layer` |
| Version | `3.11.0` |
| Port | `8084` |
| Digest | `sha256:ca46e4a84d6ade3917d9d559ad2fe3ba7fa5269cbf27d2d0ad7c473ba104d371` |

## Local run

```bash
cd apps/sla-agent-layer
python -m uvicorn src.main:app --host 0.0.0.0 --port 8084
```

## Documentation rule

Do not treat Kafka-primary flow, federated policies, domain agents, theoretical actuation, or research-only models as active runtime unless the canonical operational document classifies them as active.
