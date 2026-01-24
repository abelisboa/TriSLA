# SLA-Agent Layer

**Role.** SLA-Agent implements lifecycle-level actions and monitoring hooks after an SLA request is processed. It consumes decision outputs and can orchestrate subsequent control-plane actions required by the platform (e.g., invoking NASP workflows, recording lifecycle transitions, emitting monitoring signals).

## Responsibilities
- Consume decisions and correlate with SLA identifiers
- Trigger platform actions when required (e.g., activation, monitoring setup)
- Provide lifecycle state transitions and operational logs

## Integration points
- Kafka (decision events)
- NASP Adapter (platform integration)
- Observability stack (metrics/traces)

## Observability
- Prometheus counters for processed decisions and lifecycle transitions
- Trace spans for action execution (success/failure)

## Troubleshooting
- If the agent does not react to decisions: verify Kafka connectivity, topic name, and consumer group configuration.
