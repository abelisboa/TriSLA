# SLA Lifecycle — BC-NSSMF

**Operational reference:** [`docs/modules/bc-nssmf.md`](../../modules/bc-nssmf.md)

## Production hot path

```text
1. Portal Backend receives ACCEPT from SEM admission pipeline
2. Portal orchestrates via NASP Adapter
3. If orchestration SUCCESS → Portal POST /api/v1/register-sla
4. BC-NSSMF submits SLAContract.registerSLA() to Besu
5. tx_hash + block_number returned to Portal
6. Portal composes governance metadata and PATCHes SEM (10G.4)
7. Frontend renders Governance Panel (10G.8)
```

## NOT HOT PATH — obsolete narrative

The following sequence is **not** the production commit ingress:

```text
Decision Engine → Kafka → BC-NSSMF   ← NOT STARTED / NOT HOT PATH
```

Kafka consumer code exists in `apps/bc-nssmf/src/kafka_consumer.py` but is never started. Decision Engine does not call BC-NSSMF HTTP on the frozen submit path.

For full lifecycle and governance composition, see Portal `sla.py` and [`docs/TRISLA_E2E_FLOW_CANONICAL.md`](../../TRISLA_E2E_FLOW_CANONICAL.md).
