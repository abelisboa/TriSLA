# SLA-Agent Lifecycle Execution

## Observation and evaluation

```text
Telemetry input
    │
    ├─ collect RAN, transport, and core values
    ├─ evaluate configured SLOs
    ├─ evaluate service-profile requirements
    ├─ compare with a reference snapshot when supplied
    └─ return runtime state and recommendation
```

Runtime evaluation can return compliant, warning, at-risk, or violated states according to current telemetry, supplied requirements, and detected conditions.

## Coordination

`POST /api/v1/coordinate` dispatches an action to selected domain agents or to all configured agents. `POST /api/v1/policies/federated` applies ordered domain actions and returns per-domain outcomes and a success rate.

## Actuation record lifecycle

```text
request → authorize → execute → verify
                    ├─ rollback
                    └─ expire
```

Each transition uses a request identifier. Records can be retrieved individually or listed. The public chart keeps closed-loop domain mutation disabled by default, so enabling external actions requires an explicit deployment configuration decision.

## Pipeline integration

`POST /api/v1/ingest/pipeline-event` records a submitted lifecycle event and can trigger SLO evaluation. `POST /api/v1/agent/revalidate-telemetry` provides the revalidation boundary used by the Portal Backend.

## References

- [API implementation](../../../apps/sla-agent-layer/src/main.py)
- [Coordinator](../../../apps/sla-agent-layer/src/agent_coordinator.py)
- [Runtime evaluator](../../../apps/sla-agent-layer/src/runtime_slo_evaluator.py)
