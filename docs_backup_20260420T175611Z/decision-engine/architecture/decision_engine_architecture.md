# Decision Engine Architecture

## Components

- Input Normalizer (SEM-CSMF + ML-NSMF payload alignment)
- Policy Evaluator
- Threshold Engine
- Telemetry Collector (Prometheus adapters)
- Decision Publisher (Kafka/REST)

## Data Flow

SEM-CSMF + ML-NSMF + Telemetry -> Decision Engine -> BC-NSSMF / SLA-Agent

## Responsibilities

- Fuse multi-domain inputs
- Apply admission policy thresholds
- Produce deterministic SLA decision output

