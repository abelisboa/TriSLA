# SEM-CSMF Interfaces

## 1. Integration Scope

SEM-CSMF exposes and consumes interfaces to bridge semantic intent processing with downstream SLA evaluation and prediction modules.

Primary downstream interfaces:

- I-01 (gRPC): SEM-CSMF -> Decision Engine
- I-02 (Kafka): SEM-CSMF -> ML-NSMF

## 2. I-01 (gRPC)

### Purpose

Provide structured decision metadata derived from semantically validated NEST context.

### Direction

SEM-CSMF -> Decision Engine

### Typical Endpoint

`decision-engine:50051`

### Reference Payload (conceptual)

```proto
message NESTMetadata {
  string nest_id = 1;
  string intent_id = 2;
  string tenant_id = 3;
  string service_type = 4;
  map<string, string> sla_requirements = 5;
}
```

### Operational Notes

- Use retry-enabled client variant for transient RPC failures
- Preserve correlation identifiers (`intent_id`, `nest_id`) for observability

## 3. I-02 (Kafka)

### Purpose

Publish full NEST events for model consumption and prediction workflows in ML-NSMF.

### Direction

SEM-CSMF -> ML-NSMF

### Topic

`sem-csmf-nests`

### Reference Payload (conceptual)

```json
{
  "nest_id": "nest-urllc-001",
  "intent_id": "intent-001",
  "slice_type": "URLLC",
  "sla_requirements": {
    "latency": "10ms",
    "throughput": "100Mbps",
    "reliability": 0.99999
  },
  "timestamp": "2025-01-27T10:00:00Z"
}
```

### Operational Notes

- Ensure topic provisioning and partition strategy are stable across runs
- Include semantic context fields needed by downstream predictors

## 4. Reliability and Observability

- gRPC failures: handle via retry/backoff strategy
- Kafka failures: handle with producer retries and broker health checks
- Emit trace spans for:
  - `send_i01`
  - `send_i02`

## 5. Interface Summary

The interface layer operationalizes the semantic contract produced by SEM-CSMF. It guarantees that downstream modules consume validated and structured intent artifacts, enabling coherent SLA evaluation and reproducible experimentation.
