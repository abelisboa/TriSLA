# SLA-Agent Architecture

## Component view

```text
Portal Backend and platform services
                 │ HTTP :8084
                 ▼
          SLA-Agent FastAPI
                 │
       ┌─────────┼─────────┐
       ▼         ▼         ▼
   RAN agent  Transport  Core agent
       └─────────┼─────────┘
                 ▼
        Agent Coordinator
                 │
        runtime evaluation
                 │
        actuation record flow
```

The FastAPI layer exposes health, metrics, domain operations, coordination, runtime evaluation, revalidation, and actuation records. `AgentCoordinator` selects domain agents, aggregates results, and evaluates configured SLOs.

Runtime evaluation consumes telemetry and SLA requirements, computes domain and service-profile conditions, detects drift when a reference snapshot is supplied, and returns a state and recommendation.

## Dependencies

The Helm Deployment configures:

- NASP Adapter at port `8085`;
- BC-NSSMF at port `8083`;
- Kafka brokers when event transport is enabled;
- Prometheus for current telemetry queries in the live deployment;
- an OTLP endpoint for traces.

## Deployment

The service is `ClusterIP` on port `8084`. The container uses the same port. Liveness and readiness both call `/health`. The current chart defaults keep domain mutation disabled while retaining actuation record endpoints.

## References

- [Application entrypoint](../../../apps/sla-agent-layer/src/main.py)
- [Agent coordinator](../../../apps/sla-agent-layer/src/agent_coordinator.py)
- [Runtime evaluator](../../../apps/sla-agent-layer/src/runtime_slo_evaluator.py)
- [Helm Deployment](../../../helm/trisla/templates/deployment-sla-agent-layer.yaml)
