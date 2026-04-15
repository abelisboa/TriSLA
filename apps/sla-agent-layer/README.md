# SLA-Agent Layer

Federated agent module for SLA management in TriSLA.

## Overview

O SLA-Agent Layer implementa agentes autônomos para domínios RAN, Transport e Core, com coordenação federada e políticas distribuídas.

## Architecture

### Main Components

- **AgentRAN**: Agent for the RAN domain (Radio Access Network)
- **AgentTransport**: Agent for the Transport domain
- **AgentCore**: Agent for the Core domain
- **AgentCoordinator**: Federated agent coordinator
- **SLOEvaluator**: SLO evaluator (Service Level Objectives)
- **ActionConsumer**: Kafka consumer for Decision Engine decisions (I-05)
- **EventProducer**: Kafka producer for I-06 and I-07 events

### Interfaces

- **I-05**: Decision consumption from Decision Engine via Kafka
- **I-06**: Publishing SLO violation/risk events and action coordination
- **I-07**: Publishing executed action results

## Federated Policies

Federated policies allow coordinated actions across multiple domains:

```python
policy = {
    "name": "multi-domain-policy",
    "priority": "high",
    "actions": [
        {
            "domain": "RAN",
            "action": {"type": "ADJUST_PRB", "parameters": {...}},
            "depends_on": []  # No dependencies
        },
        {
            "domain": "Transport",
            "action": {"type": "ADJUST_BANDWIDTH", "parameters": {...}},
            "depends_on": ["RAN"]  # Depends on RAN
        }
    ]
}
```

### Characteristics

- **Execution Order**: Topological ordering based on dependencies
- **Priorities**: Policies can have high, medium, or low priority
- **Dependencies**: Actions can depend on other actions across domains
- **Coordination**: Coordinated execution across multiple agents

## Agent Coordination

The `AgentCoordinator` manages coordination among agents:

### Capabilities

1. **Action Coordination**: Executes actions across multiple domains simultaneously
2. **Aggregated Collection**: Collects metrics from all agents
3. **Aggregated Evaluation**: Evaluates SLOs from all domains
4. **Federated Policies**: Applies policies involving multiple domains

### Usage Example

```python
# Coordinate action across multiple domains
action = {
    "type": "ADJUST_RESOURCES",
    "parameters": {"resource_level": 0.8}
}

result = await coordinator.coordinate_action(
    action,
    target_domains=["RAN", "Transport"]
)
```

## SLOs (Service Level Objectives)

Each domain has SLOs configured in YAML files:

- `src/config/slo_ran.yaml`: SLOs para RAN
- `src/config/slo_transport.yaml`: SLOs para Transport
- `src/config/slo_core.yaml`: SLOs para Core

### SLO Status

- **OK**: Metric within target
- **RISK**: Metric near limit (risk threshold)
- **VIOLATED**: Metric violated target

## API REST

### Endpoints

- `GET /health`: Agent health check
- `POST /api/v1/agents/ran/collect`: Collect RAN metrics
- `POST /api/v1/agents/ran/action`: Execute RAN action
- `POST /api/v1/agents/transport/collect`: Collect Transport metrics
- `POST /api/v1/agents/transport/action`: Execute Transport action
- `POST /api/v1/agents/core/collect`: Collect Core metrics
- `POST /api/v1/agents/core/action`: Execute Core action
- `GET /api/v1/metrics/realtime`: Real-time metrics from all domains
- `GET /api/v1/slos`: SLOs and compliance status
- `POST /api/v1/coordinate`: Coordinate action across multiple domains (I-06)
- `POST /api/v1/policies/federated`: Apply federated policy (I-06)

## NASP Integration

O SLA-Agent Layer integra com o NASP Adapter para:

- Collection of real metrics from NASP
- Execution of corrective actions in NASP
- Real-time SLO monitoring

### Degraded Mode

If NASP Adapter is unavailable, the system operates in degraded mode with stub metrics.

## Kafka Integration

### Topics

- `trisla-i05-actions`: Decisions from Decision Engine (consumer)
- `trisla-i06-agent-events`: SLO violation/risk events (publisher)
- `trisla-i07-agent-actions`: Executed action results (publisher)

### Configuration

Environment variables:

- `KAFKA_ENABLED`: Enable Kafka (default: false)
- `KAFKA_BROKERS`: Kafka broker list (comma-separated)
- `KAFKA_BOOTSTRAP_SERVERS`: Bootstrap servers (default: localhost:29092,kafka:9092)

## Tests

### Unit Tests

```bash
pytest tests/unit/test_sla_agent_layer_agents.py -v
pytest tests/unit/test_sla_agent_layer_coordinator.py -v
```

### Integration Tests

```bash
pytest tests/integration/test_sla_agent_layer_integration.py -v
```

### E2E Tests

```bash
pytest tests/integration/test_sla_agent_layer_e2e.py -v
```

## Local Execution

```bash
cd apps/sla-agent-layer
python -m uvicorn src.main:app --host 0.0.0.0 --port 8084
```

## Docker

```bash
docker build -t trisla-sla-agent-layer:latest -f apps/sla-agent-layer/Dockerfile .
docker run -p 8084:8084 trisla-sla-agent-layer:latest
```

## Observability

SLA-Agent Layer supports OpenTelemetry (OTLP) for distributed observability.

Environment variables:

- `OTLP_ENABLED`: Enable OTLP (default: false)
- `OTLP_ENDPOINT`: OTLP Collector endpoint (default: http://otlp-collector:4317)

## Version

v3.7.6 (FASE A)






