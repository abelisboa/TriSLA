# SLA-Agent Layer Complete Guide

**Version:** v3.9.3  
**Last Updated:** 2024-01-24  
**Status:** Production Ready

## Table of Contents

1. [Module Purpose and Design Rationale](#1-module-purpose-and-design-rationale)
2. [Internal Architecture](#2-internal-architecture)
3. [Execution Flow](#3-execution-flow-step-by-step)
4. [SLO Compliance State Machine](#4-slo-compliance-state-machine)
5. [Data Models and Event Payloads](#5-data-models-and-event-payloads)
6. [Integration with Other TriSLA Modules](#6-integration-with-other-trisla-modules)
7. [Deployment and Configuration](#7-deployment-and-configuration)
8. [Observability and Evidence](#8-observability-and-evidence)
9. [Failure Modes and Resolved Issues](#9-failure-modes-and-resolved-issues)
10. [Reproducibility Notes](#10-reproducibility-notes)

---

## 1. Module Purpose and Design Rationale

### Why the SLA-Agent Exists

The SLA-Agent Layer exists as a separate control-plane component in TriSLA to bridge the gap between admission decisions (made by the Decision Engine) and operational platform actions. After an SLA request is admitted, the system must:

1. **Coordinate Platform Actions**: Execute control-plane actions across multiple network domains (RAN, Transport, Core) to activate and monitor the admitted SLA
2. **Monitor Ongoing Compliance**: Continuously evaluate Service Level Objectives (SLOs) against real-time infrastructure metrics
3. **Emit Lifecycle Events**: Publish agent events and action results for downstream consumers (e.g., BC-NSSMF, observability systems)
4. **Integrate with NASP**: Collect real-time metrics from the NASP platform via the NASP Adapter

### Why It Is a Separate Module

The SLA-Agent Layer is intentionally separated from other TriSLA modules for the following reasons:

- **Separation of Concerns**: The Decision Engine focuses on admission control (ACCEPT/REJECT/RENEG), while the SLA-Agent focuses on post-admission lifecycle management
- **Asynchronous Operation**: The SLA-Agent operates asynchronously via event-driven architecture, consuming decision events from Kafka and executing actions independently
- **Federated Architecture**: The SLA-Agent implements a federated agent model with separate agents per network domain (RAN, Transport, Core), each with domain-specific logic
- **Non-Real-Time Nature**: Unlike the Decision Engine which must respond synchronously to admission requests, the SLA-Agent operates in a non-real-time manner, processing events as they arrive

### Role in the SLA Lifecycle

The SLA-Agent Layer operates in the **post-decision phase** of the SLA lifecycle:

1. **Decision Phase** (Decision Engine): Admission decision is made (ACCEPT/REJECT/RENEG)
2. **Lifecycle Phase** (SLA-Agent): 
   - Consumes decision events from Kafka topic `trisla-i05-actions`
   - Coordinates platform actions across network domains
   - Monitors SLO compliance continuously
   - Publishes lifecycle events to Kafka topics `trisla-i06-agent-events` and `trisla-i07-agent-actions`

---

## 2. Internal Architecture

### Component Overview

The SLA-Agent Layer is implemented in `apps/sla-agent-layer/src/` with the following components:

#### Core Components

1. **ActionConsumer** (`src/kafka_consumer.py`)
   - Kafka consumer for decision events (topic: `trisla-i05-actions`)
   - Consumer group: `sla-agents-i05-consumer`
   - Deserializes JSON payloads and routes to appropriate agents

2. **EventProducer** (`src/kafka_producer.py`)
   - Kafka producer for agent events
   - Topics: `trisla-i06-agent-events` (violation/risk events), `trisla-i07-agent-actions` (action results)
   - Implements retry logic with exponential backoff

3. **AgentCoordinator** (`src/agent_coordinator.py`)
   - Coordinates actions across federated domains
   - Manages multi-domain action execution
   - Aggregates metrics from all agents

4. **Federated Agents**
   - **AgentRAN** (`src/agent_ran.py`): RAN domain agent
   - **AgentTransport** (`src/agent_transport.py`): Transport domain agent
   - **AgentCore** (`src/agent_core.py`): Core domain agent

5. **SLOEvaluator** (`src/slo_evaluator.py`)
   - Evaluates metrics against configured SLOs
   - Determines compliance status: `OK`, `RISK`, `VIOLATED`
   - Calculates compliance rates per domain

6. **Observability** (`src/observability/`)
   - **metrics.py**: Prometheus metrics (counters, histograms, gauges)
   - **tracing.py**: OpenTelemetry distributed tracing
   - **tracing_base.py**: Base tracing utilities

### Execution Model

The SLA-Agent Layer operates in an **asynchronous, event-driven** model:

- **Event Consumption**: `ActionConsumer` continuously polls Kafka topic `trisla-i05-actions` for decision events
- **Event Processing**: Each decision event is deserialized, validated, and routed to the appropriate agent(s) based on domain requirements
- **Action Execution**: Agents execute actions asynchronously (e.g., collect metrics from NASP Adapter, evaluate SLOs)
- **Event Production**: Results and lifecycle events are published to Kafka topics asynchronously

### Runtime Dependencies

- **Kafka**: Required for consuming decision events and producing agent events
- **NASP Adapter**: Required for collecting real-time infrastructure metrics
- **OpenTelemetry Collector**: Required for distributed tracing (optional but recommended)
- **Prometheus**: Required for metrics scraping (optional but recommended)

### In-Memory State Management

The SLA-Agent Layer maintains minimal in-memory state:

- **Agent Instances**: AgentRAN, AgentTransport, AgentCore instances are created at startup and maintained in memory
- **NASP Client**: NASP Adapter client instances are created per agent and cached
- **SLO Configuration**: SLO configurations are loaded at startup and maintained in memory
- **Kafka Consumer/Producer**: Kafka client instances are maintained for the lifetime of the service

**Note**: The SLA-Agent Layer is **stateless** with respect to SLA lifecycle state. Lifecycle state is managed externally (e.g., by BC-NSSMF or a state store), not by the SLA-Agent itself.

### Correlation Mechanisms

The SLA-Agent Layer correlates events using the following identifiers:

- **intent_id**: Unique identifier for the SLA intent (from SEM-CSMF)
- **decision_id**: Unique identifier for the admission decision (from Decision Engine)
- **sla_id**: Unique identifier for the SLA instance (generated after admission)
- **agent_id**: Unique identifier for the agent instance (format: `{domain}-{uuid}`)

These identifiers are propagated through:
- Kafka message keys (for partitioning)
- OpenTelemetry trace attributes
- Prometheus metric labels
- Log entries

---

## 3. Execution Flow (Step-by-Step)

### Decision Event Consumption Flow

The following is the step-by-step execution flow when a decision event is received:

1. **Decision Event Production** (Decision Engine)
   - Decision Engine produces a decision event to Kafka topic `trisla-i05-actions`
   - Event payload contains: `decision_id`, `intent_id`, `decision` (ACCEPT/REJECT/RENEG), `justification`, `timestamp`

2. **Kafka Consumer Polling** (ActionConsumer)
   - `ActionConsumer.poll()` continuously polls Kafka topic `trisla-i05-actions`
   - Polling interval: 1 second (configurable via `consumer_timeout_ms`)
   - Consumer group: `sla-agents-i05-consumer`

3. **Event Deserialization** (ActionConsumer)
   - Raw Kafka message is deserialized from JSON
   - Message structure is validated
   - OpenTelemetry span is created with attributes: `kafka.topic`, `kafka.partition`, `kafka.offset`

4. **Event Routing** (ActionConsumer)
   - Decision event is analyzed to determine target domains (RAN, Transport, Core)
   - Event is routed to `AgentCoordinator.coordinate_action()`

5. **Action Coordination** (AgentCoordinator)
   - `AgentCoordinator` determines which agents should execute the action
   - For each target domain, the corresponding agent is invoked:
     - `AgentRAN.execute_action(action)` for RAN domain
     - `AgentTransport.execute_action(action)` for Transport domain
     - `AgentCore.execute_action(action)` for Core domain

6. **Agent Action Execution** (AgentRAN/AgentTransport/AgentCore)
   - Agent receives action request
   - Agent collects metrics from NASP Adapter (if NASP integration is enabled):
     - `AgentRAN`: Calls `nasp_client.get_ran_metrics()`
     - `AgentTransport`: Calls `nasp_client.get_transport_metrics()`
     - `AgentCore`: Calls `nasp_client.get_core_metrics()`
   - Agent normalizes metrics to standard format
   - Agent evaluates SLOs using `SLOEvaluator.evaluate(metrics)`

7. **SLO Evaluation** (SLOEvaluator)
   - Metrics are evaluated against configured SLOs
   - For each SLO, status is determined: `OK`, `RISK`, or `VIOLATED`
   - Overall compliance rate is calculated
   - Evaluation result is returned to the agent

8. **Event Production** (EventProducer)
   - If SLO violation or risk is detected, agent publishes event to Kafka topic `trisla-i06-agent-events`
   - Event payload contains: `agent_id`, `domain`, `status` (OK/RISK/VIOLATED), `metrics`, `timestamp`
   - Action result is published to Kafka topic `trisla-i07-agent-actions`
   - Event payload contains: `agent_id`, `action`, `result`, `timestamp`

9. **Observability Signals** (Observability)
   - Prometheus metrics are updated:
     - `trisla_sla_requests_total` (counter)
     - `trisla_sla_violations_total` (counter)
     - `trisla_sla_active_contracts` (gauge)
   - OpenTelemetry spans are completed and exported
   - Structured logs are emitted with correlation IDs

### Continuous Monitoring Flow

In addition to processing decision events, the SLA-Agent Layer continuously monitors SLO compliance:

1. **Metric Collection** (Periodic)
   - Each agent periodically collects metrics from NASP Adapter
   - Collection interval: Configurable (default: 30 seconds)

2. **SLO Evaluation** (Periodic)
   - Collected metrics are evaluated against configured SLOs
   - Evaluation result determines status: `OK`, `RISK`, or `VIOLATED`

3. **Violation Detection** (Event-Driven)
   - If `VIOLATED` status is detected, agent publishes violation event to Kafka topic `trisla-i06-agent-events`
   - Violation event triggers downstream actions (e.g., alerting, remediation)

4. **Observability Updates** (Continuous)
   - Prometheus metrics are continuously updated
   - OpenTelemetry traces are generated for each evaluation cycle

---

## 4. SLO Compliance State Machine

The SLA-Agent Layer uses a **SLO compliance state machine** (not a traditional SLA lifecycle state machine). The states represent the compliance status of SLOs, not the lifecycle state of the SLA itself.

### States

The SLO compliance state machine has three states:

1. **OK**: All SLOs are within target thresholds
2. **RISK**: One or more SLOs are approaching threshold limits (configurable risk threshold, default: 80% of target)
3. **VIOLATED**: One or more SLOs have exceeded target thresholds

### State Transitions

```
OK ──[SLO approaching threshold]──> RISK
OK ──[SLO exceeds target]─────────> VIOLATED
RISK ──[SLO returns to target]─────> OK
RISK ──[SLO exceeds target]────────> VIOLATED
VIOLATED ──[SLO returns to target]─> OK
```

### Entry Conditions

- **OK**: All SLOs are within target thresholds (e.g., latency ≤ 10ms, throughput ≥ 1000 Mbps)
- **RISK**: At least one SLO is between risk threshold and target (e.g., latency between 8ms and 10ms when target is 10ms)
- **VIOLATED**: At least one SLO has exceeded target threshold (e.g., latency > 10ms)

### Triggering Events

- **Metric Collection**: Periodic collection of metrics from NASP Adapter triggers SLO evaluation
- **SLO Evaluation**: `SLOEvaluator.evaluate(metrics)` determines current state
- **State Change**: State transition occurs when evaluation result differs from previous state

### Side Effects

- **OK State**: No side effects (normal operation)
- **RISK State**: Warning event may be published to Kafka topic `trisla-i06-agent-events` (optional, configurable)
- **VIOLATED State**: Violation event is published to Kafka topic `trisla-i06-agent-events`, Prometheus counter `trisla_sla_violations_total` is incremented

### Emitted Signals

- **Kafka Events**: State changes trigger events on topic `trisla-i06-agent-events`
- **Prometheus Metrics**: State is reflected in metric labels and counters
- **OpenTelemetry Traces**: State transitions are recorded in trace attributes
- **Structured Logs**: State changes are logged with correlation IDs

---

## 5. Data Models and Event Payloads

### Kafka Decision Event Schema (I-05)

The Decision Engine produces decision events to Kafka topic `trisla-i05-actions` with the following schema:

```json
{
  "decision_id": "decision-uuid-123",
  "intent_id": "intent-uuid-456",
  "decision": "ACCEPT",
  "justification": {
    "ml_score": 0.85,
    "ml_confidence": 0.92,
    "infrastructure_signals": {
      "cpu_available": 0.65,
      "memory_available": 0.70,
      "disk_available": 0.80
    }
  },
  "timestamp": "2024-01-24T10:30:00Z",
  "metadata": {
    "slice_type": "eMBB",
    "requirements": {
      "latency": 10,
      "throughput": 1000
    }
  }
}
```

### Kafka Agent Event Schema (I-06)

The SLA-Agent Layer produces agent events to Kafka topic `trisla-i06-agent-events` with the following schema:

```json
{
  "agent_id": "ran-uuid-789",
  "domain": "RAN",
  "event_type": "SLO_VIOLATION",
  "status": "VIOLATED",
  "metrics": {
    "latency": 12.5,
    "throughput": 850.0,
    "prb_allocation": 0.75
  },
  "slos": [
    {
      "name": "latency",
      "target": 10.0,
      "current": 12.5,
      "unit": "ms",
      "status": "VIOLATED",
      "compliance": false
    }
  ],
  "compliance_rate": 0.67,
  "timestamp": "2024-01-24T10:35:00Z",
  "correlation": {
    "intent_id": "intent-uuid-456",
    "decision_id": "decision-uuid-123",
    "sla_id": "sla-uuid-abc"
  }
}
```

### Kafka Action Result Schema (I-07)

The SLA-Agent Layer produces action results to Kafka topic `trisla-i07-agent-actions` with the following schema:

```json
{
  "agent_id": "ran-uuid-789",
  "domain": "RAN",
  "action": {
    "type": "ADJUST_PRB_ALLOCATION",
    "parameters": {
      "prb_increase": 0.10
    }
  },
  "result": {
    "executed": true,
    "success": true,
    "message": "PRB allocation increased by 10%"
  },
  "timestamp": "2024-01-24T10:36:00Z",
  "correlation": {
    "intent_id": "intent-uuid-456",
    "decision_id": "decision-uuid-123",
    "sla_id": "sla-uuid-abc"
  }
}
```

### SLA Identifiers and Correlation Keys

- **intent_id**: UUID generated by SEM-CSMF during intent processing
- **decision_id**: UUID generated by Decision Engine during admission decision
- **sla_id**: UUID generated after admission (may be generated by BC-NSSMF or external system)
- **agent_id**: Format: `{domain}-{uuid}` (e.g., `ran-550e8400-e29b-41d4-a716-446655440000`)

### NASP Metrics Format

Metrics collected from NASP Adapter are normalized to a standard format:

```json
{
  "domain": "RAN",
  "metrics": {
    "latency": 12.5,
    "throughput": 850.0,
    "prb_allocation": 0.75,
    "cpu_utilization": 0.65,
    "memory_utilization": 0.70
  },
  "timestamp": "2024-01-24T10:35:00Z"
}
```

---

## 6. Integration with Other TriSLA Modules

### Decision Engine Integration

**Integration Point**: Kafka topic `trisla-i05-actions`

- **Direction**: Decision Engine → SLA-Agent Layer
- **Protocol**: Kafka (asynchronous)
- **Consumer Group**: `sla-agents-i05-consumer`
- **Event Schema**: See [Data Models Section](#5-data-models-and-event-payloads)

**Implementation Details**:
- Consumer is implemented in `src/kafka_consumer.py` (class `ActionConsumer`)
- Consumer polls topic continuously with 1-second timeout
- Events are deserialized from JSON and routed to agents

### NASP Adapter Integration

**Integration Point**: HTTP REST API

- **Direction**: SLA-Agent Layer → NASP Adapter
- **Protocol**: HTTP REST (synchronous)
- **Base URL**: Configured via environment variable `NASP_ADAPTER_URL` (default: `http://trisla-nasp-adapter:8080`)
- **Endpoints**:
  - `GET /api/v1/metrics/ran` - RAN domain metrics
  - `GET /api/v1/metrics/transport` - Transport domain metrics
  - `GET /api/v1/metrics/core` - Core domain metrics

**Implementation Details**:
- NASP client is implemented in each agent (`AgentRAN`, `AgentTransport`, `AgentCore`)
- Client is instantiated at agent startup and cached
- Metrics are collected periodically (default: 30 seconds) or on-demand
- Metrics are normalized to standard format before SLO evaluation

**Error Handling**:
- If NASP Adapter is unavailable, agents fall back to mock metrics (configurable)
- Errors are logged and reported via OpenTelemetry traces
- Retry logic is implemented with exponential backoff

### BC-NSSMF Integration

**Integration Point**: HTTP REST API (optional)

- **Direction**: SLA-Agent Layer → BC-NSSMF (if enabled)
- **Protocol**: HTTP REST (synchronous)
- **Base URL**: Configured via environment variable `BC_NSSMF_URL` (default: `http://trisla-bc-nssmf:8080`)
- **Purpose**: On-chain registration of lifecycle events (if blockchain governance is enabled)

**Implementation Details**:
- BC-NSSMF integration is **optional** and disabled by default
- Integration is triggered when lifecycle events occur (e.g., SLO violations)
- Events are sent to BC-NSSMF for on-chain registration

**Note**: BC-NSSMF integration is not currently implemented in the SLA-Agent Layer codebase. This integration is handled separately by other components.

### Observability Stack Integration

**Prometheus Integration**:
- **Metrics Endpoint**: `GET /metrics` (exposed on port 8084)
- **Metrics Exposed**:
  - `trisla_sla_requests_total` (counter): Total SLA requests processed
  - `trisla_sla_violations_total` (counter): Total SLO violations detected
  - `trisla_sla_active_contracts` (gauge): Number of active SLA contracts
  - `trisla_sla_compile_latency_ms` (histogram): Contract compilation latency

**OpenTelemetry Integration**:
- **OTLP Endpoint**: Configured via environment variable `OTLP_ENDPOINT` (default: `http://trisla-otel-collector:4317`)
- **Protocol**: gRPC (OTLP)
- **Traces Generated**:
  - `kafka_consumer.poll` - Kafka consumer polling
  - `coordinate_action` - Action coordination
  - `collect_metrics` - Metric collection
  - `evaluate_slos` - SLO evaluation
  - `execute_action` - Action execution

**Implementation Details**:
- Metrics are implemented in `src/observability/metrics.py`
- Tracing is implemented in `src/observability/tracing.py`
- Both are initialized at service startup in `src/main.py`

---

## 7. Deployment and Configuration

### Helm Deployment

The SLA-Agent Layer is deployed via Helm chart `helm/trisla` under the `slaAgentLayer` section.

**Helm Values** (`helm/trisla/values.yaml`):

```yaml
slaAgentLayer:
  enabled: true
  image:
    repository: trisla-sla-agent-layer
    tag: v3.9.3
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 8084
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 2000m
      memory: 2Gi
  replicas: 3
```

**Deployment Template: `helm/trisla/templates/deployment-sla-agent-layer.yaml`**

### Environment Variables

#### Required Environment Variables

- **NASP_ADAPTER_URL**: NASP Adapter service URL (default: `http://trisla-nasp-adapter:8080`)
- **OTLP_ENDPOINT**: OpenTelemetry collector endpoint (default: `http://trisla-otel-collector:4317`)

#### Optional Environment Variables

- **KAFKA_ENABLED**: Enable Kafka integration (default: `false`)
- **KAFKA_BROKERS**: Kafka broker addresses (comma-separated, default: empty)
- **KAFKA_BOOTSTRAP_SERVERS**: Kafka bootstrap servers (default: `localhost:29092,kafka:9092`)
- **KAFKA_MAX_RETRIES**: Maximum retries for Kafka producer (default: `3`)
- **KAFKA_RETRY_DELAY**: Initial retry delay in seconds (default: `1.0`)
- **KAFKA_RETRY_BACKOFF**: Retry backoff multiplier (default: `2.0`)
- **BC_NSSMF_URL**: BC-NSSMF service URL (default: `http://trisla-bc-nssmf:8080`)
- **TRISLA_NODE_INTERFACE**: Network interface name (default: `my5g`)
- **TRISLA_NODE_IP**: Node IP address (default: from network configuration)

### Default Behaviors

**When Kafka is Disabled**:
- `ActionConsumer` starts in offline mode
- No decision events are consumed
- Service continues to operate (health checks, metrics collection still work)

**When NASP Adapter is Unavailable**:
- Agents fall back to mock metrics (if configured)
- SLO evaluation continues with mock data
- Errors are logged and reported via OpenTelemetry

**When BC-NSSMF is Unavailable**:
- Lifecycle events are not registered on-chain
- Service continues to operate normally
- Events are still published to Kafka topics

### Health Checks

- **Liveness Probe**: `GET /health` (initial delay: 30s, period: 10s)
- **Readiness Probe**: `GET /health` (initial delay: 10s, period: 5s)

Health endpoint returns:

```json
{
  "status": "healthy",
  "module": "sla-agent-layer",
  "agents": {
    "ran": true,
    "transport": true,
    "core": true
  }
}
```

---

## 8. Observability and Evidence

### Prometheus Metrics

The SLA-Agent Layer exposes Prometheus metrics at the `/metrics` endpoint.

#### Counters

- **trisla_sla_requests_total**: Total SLA requests processed
  - Labels: `contract_type`, `status`
  - Example: `trisla_sla_requests_total{contract_type="slice_sla",status="success"} 42`

- **trisla_sla_violations_total**: Total SLO violations detected
  - Labels: `severity`, `contract_id`
  - Example: `trisla_sla_violations_total{severity="critical",contract_id="sla-uuid-abc"} 5`

#### Histograms

- **trisla_sla_compile_latency_ms**: Contract compilation latency in milliseconds
  - Buckets: `[50.0, 100.0, 150.0, 200.0, 500.0, 1000.0, +Inf]`
  - Example: `trisla_sla_compile_latency_ms_bucket{le="100.0"} 38`

#### Gauges

- **trisla_sla_active_contracts**: Number of active SLA contracts
  - Example: `trisla_sla_active_contracts 12`

### OpenTelemetry Traces

The SLA-Agent Layer generates OpenTelemetry traces for the following operations:

- **kafka_consumer.poll**: Kafka consumer polling cycle
  - Attributes: `kafka.topic`, `kafka.partition`, `kafka.offset`

- **coordinate_action**: Action coordination across domains
  - Attributes: `action.type`, `coordination.executed_count`, `coordination.total_count`

- **collect_metrics**: Metric collection from NASP Adapter
  - Attributes: `metrics.domain`, `metrics.collected`

- **evaluate_slos**: SLO evaluation
  - Attributes: `slo.domain`, `slo.count`, `slo.compliance_rate`

- **execute_action**: Action execution
  - Attributes: `action.domain`, `action.executed`, `action.success`

### Logs Generated During Lifecycle Transitions

The SLA-Agent Layer emits structured logs (JSON format) for the following events:

- **Consumer Initialization**: `"✅ Consumer I-05 criado para tópico: trisla-i05-actions"`
- **Event Processing**: `"Processing decision event: {decision_id}"`
- **SLO Violation**: `"SLO violation detected: {domain}, {slo_name}, {status}"`
- **Action Execution**: `"Action executed: {domain}, {action_type}, {result}"`
- **Error Events**: `"❌ Erro ao executar ação em {domain}: {error}"`

### How to Verify SLA-Agent is Running Correctly

1. **Health Check**: `curl http://trisla-sla-agent-layer:8084/health`
   - Expected: `{"status": "healthy", "module": "sla-agent-layer", "agents": {...}}`

2. **Metrics Endpoint**: `curl http://trisla-sla-agent-layer:8084/metrics`
   - Expected: Prometheus metrics in text format

3. **Kafka Consumer Status**: Check logs for `"✅ Consumer I-05 criado para tópico: trisla-i05-actions"`
   - If Kafka is disabled, expect: `"Kafka desabilitado"`

4. **Agent Health**: Check individual agent health via `/health` endpoint
   - Expected: All agents (`ran`, `transport`, `core`) return `true`

5. **OpenTelemetry Traces**: Query traces for `sla-agent-layer` service
   - Expected: Traces for `kafka_consumer.poll`, `coordinate_action`, `collect_metrics`

---

## 9. Failure Modes and Resolved Issues

### Issue 1: Kafka Consumer Not Receiving Events

**Symptoms**:
- Decision events are produced by Decision Engine but not consumed by SLA-Agent
- No lifecycle transitions occur
- Logs show: `"⚠️ Consumer I-05 não disponível"`

**Root Cause**:
- Kafka integration disabled (`KAFKA_ENABLED=false`)
- Kafka brokers not reachable
- Consumer group misconfiguration
- Topic name mismatch

**Resolution Applied**:
1. Verify `KAFKA_ENABLED=true` in environment variables
2. Verify `KAFKA_BROKERS` contains valid broker addresses
3. Verify topic name matches: `trisla-i05-actions`
4. Verify consumer group: `sla-agents-i05-consumer`
5. Check Kafka broker connectivity: `telnet kafka 9092`

**Prevention**:
- Add health check for Kafka consumer status
- Add metrics for consumer lag
- Add alerts for consumer failures

### Issue 2: NASP Adapter Connection Failures

**Symptoms**:
- Metrics collection fails
- SLO evaluation uses mock data
- Logs show: `"❌ Erro ao coletar métricas de {domain}: {error}"`

**Root Cause**:
- NASP Adapter service unavailable
- Network connectivity issues
- Incorrect `NASP_ADAPTER_URL` configuration

**Resolution Applied**:
1. Verify NASP Adapter service is running: `kubectl get pods -l app=trisla-nasp-adapter`
2. Verify `NASP_ADAPTER_URL` is correct: `http://trisla-nasp-adapter:8080`
3. Check network connectivity: `curl http://trisla-nasp-adapter:8080/health`
4. Implement retry logic with exponential backoff
5. Fall back to mock metrics if NASP Adapter is unavailable (configurable)

**Prevention**:
- Add circuit breaker for NASP Adapter calls
- Add metrics for NASP Adapter availability
- Add alerts for NASP Adapter failures

### Issue 3: SLO Evaluation False Positives

**Symptoms**:
- SLO violations detected when metrics are within target
- Compliance rate incorrectly calculated
- Incorrect state transitions (OK → VIOLATED)

**Root Cause**:
- SLO operator mismatch (using `<=` for throughput instead of `>=`)
- Risk threshold misconfiguration
- Metric normalization errors

**Resolution Applied**:
1. Verify SLO operator matches metric type:
   - Latency: `<=` (lower is better)
   - Throughput: `>=` (higher is better)
2. Verify risk threshold: Default 80% of target
3. Verify metric normalization: Ensure metrics are in correct units
4. Add unit tests for SLO evaluation logic

**Prevention**:
- Add validation for SLO configuration
- Add unit tests for edge cases
- Add integration tests for SLO evaluation

### Issue 4: Kafka Producer Retry Failures

**Symptoms**:
- Agent events not published to Kafka
- Logs show: `"⚠️ Tentativa {attempt}/{MAX_RETRIES} falhou ao enviar para {topic}: {error}"`
- Events lost after max retries

**Root Cause**:
- Kafka broker unavailable
- Network partition
- Topic does not exist
- Producer configuration errors

**Resolution Applied**:
1. Verify Kafka broker availability
2. Verify topic exists: `trisla-i06-agent-events`, `trisla-i07-agent-actions`
3. Increase retry count: `KAFKA_MAX_RETRIES=5`
4. Increase retry delay: `KAFKA_RETRY_DELAY=2.0`
5. Add dead letter queue for failed events (future enhancement)

**Prevention**:
- Add metrics for producer failures
- Add alerts for producer retry exhaustion
- Implement dead letter queue for failed events

---

## 10. Reproducibility Notes

### Preconditions for SLA-Agent to Function

1. **Kubernetes Cluster**: SLA-Agent Layer requires a Kubernetes cluster (single-node or multi-node)
2. **Kafka**: Kafka cluster must be deployed and accessible (if Kafka integration is enabled)
3. **NASP Adapter**: NASP Adapter service must be deployed and accessible
4. **OpenTelemetry Collector**: OpenTelemetry collector must be deployed (optional but recommended)
5. **Prometheus**: Prometheus must be deployed for metrics scraping (optional but recommended)

### Dependencies on Other Modules

- **Decision Engine**: Must be deployed and producing decision events to Kafka topic `trisla-i05-actions`
- **NASP Adapter**: Must be deployed and exposing metrics endpoints
- **OpenTelemetry Collector**: Must be deployed for distributed tracing (optional)
- **Prometheus**: Must be deployed for metrics scraping (optional)

### Order of Deployment

Recommended deployment order:

1. **Observability Stack**: Deploy Prometheus and OpenTelemetry collector
2. **Kafka**: Deploy Kafka cluster
3. **NASP Adapter**: Deploy NASP Adapter service
4. **Decision Engine**: Deploy Decision Engine (must produce events before SLA-Agent can consume)
5. **SLA-Agent Layer**: Deploy SLA-Agent Layer

### Minimal Setup for Testing in Isolation

To test the SLA-Agent Layer in isolation (without full TriSLA deployment):

1. **Deploy SLA-Agent Layer**:
   ```bash
   helm upgrade --install trisla ./helm/trisla -n trisla      --set slaAgentLayer.enabled=true      --set kafka.enabled=false      --set naspAdapter.enabled=true
   ```

2. **Verify Health**:
   ```bash
   kubectl port-forward svc/trisla-sla-agent-layer 8084:8084
   curl http://localhost:8084/health
   ```

3. **Test Metrics Collection**:
   ```bash
   curl -X POST http://localhost:8084/api/v1/agents/ran/collect
   ```

4. **Test SLO Evaluation**:
   - Configure SLOs via environment variables or configuration file
   - Trigger metric collection
   - Verify SLO evaluation results

### Known Non-Reproducible Elements

The following elements are **intentionally excluded** from public reproduction:

- **Private Lab Evidence Packs**: Internal test data and evidence collections
- **Institution-Specific NASP Credentials**: NASP platform credentials and infrastructure details
- **Internal Audit Logs**: Operational logs from private lab deployments
- **Institution-Specific Configurations**: Custom Helm values for private lab environments

### Validation Checklist

To validate that the SLA-Agent Layer is functioning correctly:

- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] Metrics endpoint returns Prometheus metrics
- [ ] Kafka consumer is polling (if enabled)
- [ ] NASP Adapter metrics are collected successfully
- [ ] SLO evaluation produces correct results
- [ ] OpenTelemetry traces are generated
- [ ] Agent events are published to Kafka (if enabled)

---

## Conclusion

This guide provides comprehensive documentation of the SLA-Agent Layer implementation, architecture, and operation. The documentation is based on the actual implementation in `apps/sla-agent-layer/` and reflects real behavior, not theoretical design.

For questions or issues, refer to:
- [Architecture Overview](../../ARCHITECTURE.md)
- [Deployment Guide](../../DEPLOYMENT.md)
- [Observability Guide](../../observability/OBSERVABILITY_COMPLETE_GUIDE.md)
