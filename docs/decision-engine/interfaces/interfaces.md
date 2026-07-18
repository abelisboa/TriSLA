# Decision Engine HTTP Interface

Base port: `8082`.

## Endpoints

| Method | Path | Response |
|---|---|---|
| `GET` | `/health` | Service status, Kafka state, and gRPC listener state |
| `GET` | `/metrics` | Prometheus text format |
| `POST` | `/evaluate` | `DecisionResult` JSON |

## Evaluate an SLA

`POST /evaluate` accepts the `SLAEvaluateInput` model.

```json
{
  "intent_id": "intent-001",
  "nest_id": "nest-001",
  "intent": {
    "intent_id": "intent-001",
    "tenant_id": "tenant-001",
    "service_type": "URLLC",
    "sla_requirements": {
      "latency": "10ms",
      "reliability": 0.999
    }
  },
  "nest": {
    "nest_id": "nest-001",
    "intent_id": "intent-001",
    "network_slices": [],
    "resources": {},
    "status": "generated"
  },
  "telemetry_snapshot": {
    "ran": {"prb_utilization": 35.0},
    "transport": {"latency_ms": 8.0},
    "core": {"cpu_utilization": 40.0, "memory_utilization": 50.0}
  },
  "context": {}
}
```

Required top-level fields are `intent_id` and `intent`. `nest_id`, `nest`, `context`, `telemetry_snapshot`, and `metadata` are optional.

The response contains `decision_id`, `intent_id`, `action`, `reasoning`, `confidence`, and `timestamp`. It may also contain the NEST identifier, ML risk fields, affected domains, SLOs, and decision metadata.

Action values are:

- `AC`: accept
- `RENEG`: request revised SLA constraints
- `REJ`: reject

Example:

```bash
curl -sS http://localhost:8082/evaluate \
  -H 'Content-Type: application/json' \
  -d '{
    "intent_id":"intent-001",
    "intent":{
      "intent_id":"intent-001",
      "service_type":"eMBB",
      "sla_requirements":{"throughput":"100Mbps"}
    }
  }'
```

The implementation contract is defined in [`models.py`](../../../apps/decision-engine/src/models.py) and [`main.py`](../../../apps/decision-engine/src/main.py).
