# SLA-Agent Layer

**Role.** SLA-Agent implements lifecycle-level actions and monitoring hooks after an SLA request is processed. It consumes decision outputs and can orchestrate subsequent control-plane actions required by the platform (e.g., invoking NASP workflows, recording lifecycle transitions, emitting monitoring signals).

## Responsibilities
- Consume decisions from Kafka (decision events)
- Correlate decisions with SLA identifiers (intent_id, decision_id)
- Trigger platform actions when required (e.g., activation, monitoring setup)
- Provide lifecycle state transitions and operational logs
- Integrate with BC-NSSMF for on-chain registration (if enabled)

## Lifecycle States

The SLA-Agent manages the following lifecycle transitions:

- **PENDING**: Initial state after SLA submission
- **ACCEPTED**: Decision Engine returned ACCEPT
- **REJECTED**: Decision Engine returned REJECT
- **RENEGOTIATING**: Decision Engine returned RENEG
- **ACTIVE**: SLA is active and being monitored
- **VIOLATED**: SLA violation detected
- **TERMINATED**: SLA lifecycle ended

## Integration points
- **Kafka**: Consumes decision events from Decision Engine
- **NASP Adapter**: Invokes platform-specific actions when required
- **BC-NSSMF**: Registers SLA lifecycle events on-chain (if blockchain governance is enabled)
- **Observability stack**: Emits metrics and traces for lifecycle transitions

## Configuration

### Environment Variables
- : Kafka broker addresses (comma-separated)
- : Topic name for decision events (default: )
- : Consumer group ID (default: )
- : Enable BC-NSSMF integration (default: )
- : BC-NSSMF service URL (if enabled)

### Helm Configuration
The SLA-Agent is deployed as part of the TriSLA Helm chart under  section in .

## Observability
- **Prometheus metrics**: 
  - : Counter of processed decisions
  - : Counter of lifecycle state changes
  - : Counter of platform actions executed
- **OpenTelemetry traces**: Spans for decision consumption, lifecycle transitions, and action execution

## Runtime Behavior

The SLA-Agent operates asynchronously:
1. Consumes decision events from Kafka
2. Correlates events with SLA identifiers
3. Updates internal lifecycle state
4. Triggers platform actions if required
5. Emits observability signals

## Known Issues & Resolved Errors

### Issue: Agent does not react to decisions
**Symptom**: Decisions are produced but no lifecycle transitions occur  
**Resolution**: Verify Kafka connectivity, topic name, and consumer group configuration in Helm values

### Issue: BC-NSSMF integration fails
**Symptom**: On-chain registration errors  
**Resolution**: Verify  and  configuration, and ensure BC-NSSMF service is reachable

## Integration with Other TriSLA Modules

- **Decision Engine**: Consumes decision events via Kafka
- **BC-NSSMF**: Invokes on-chain registration when lifecycle events occur (if enabled)
- **NASP Adapter**: Calls platform APIs for activation and monitoring setup
- **Observability**: Emits metrics and traces for monitoring

## Troubleshooting

- If the agent does not react to decisions: verify Kafka connectivity, topic name, and consumer group configuration
- If lifecycle transitions are not recorded: check logs for correlation ID mismatches
- If platform actions fail: verify NASP Adapter connectivity and endpoint configuration
