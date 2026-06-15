# BC-NSSMF Architecture

**Operational reference:** [`docs/modules/bc-nssmf.md`](../../modules/bc-nssmf.md)

Architecture, commit hot path, governance runtime truth, smart contracts, and integrations are documented in the canonical module doc. This file is a pointer only — do not treat Kafka or Decision Engine as primary ingress here.

## Frozen hot path (summary)

```text
Portal Backend → POST /api/v1/register-sla → BC-NSSMF → Besu → SLAContract
```

## Non-hot-path components (not production SSOT)

- Kafka Consumer (`DecisionConsumer`) — **NOT STARTED**
- gRPC server — placeholder
- MetricsOracle — stub
- `governance_lineage.py` — **NOT WIRED**

See canonical doc for full component table and legacy paths.
