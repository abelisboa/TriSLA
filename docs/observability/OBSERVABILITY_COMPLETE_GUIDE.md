# Observability Complete Guide

This document provides comprehensive technical documentation for Observability in TriSLA, based on the real implementation.

## 1. Observability Design Principles

### Architectural First-Class Concern

Observability in TriSLA is not an afterthought or optional add-on. It is a **first-class architectural capability** designed from the ground up to:

1. **Enable Auditability**: Every decision must be traceable from intent submission to final outcome
2. **Support Reproducibility**: Metrics and traces enable third parties to reproduce experimental results
3. **Provide Transparency**: Internal behavior is observable without requiring source code access
4. **Meet Scientific Standards**: Evidence trails meet requirements for scientific publication

### Design Principles

1. **Correlation Over Isolation**: All observability signals include correlation identifiers (, , , ) to enable end-to-end traceability

2. **Evidence-Based**: Every metric, trace, and log entry maps to a concrete module, decision phase, or SLA lifecycle step

3. **Non-Intrusive**: Observability instrumentation does not alter business logic or decision outcomes

4. **Standardized**: All modules follow consistent naming conventions and instrumentation patterns

5. **Composable**: Metrics, traces, and logs can be combined to reconstruct complete decision flows

### Observability vs. Monitoring

- **Monitoring**: Reactive detection of known failure modes
- **Observability**: Proactive understanding of system behavior through metrics, traces, and logs

TriSLA emphasizes **observability** because:
- Decision outcomes are not binary (ACCEPT/REJECT) but include nuanced states (RENEG)
- Experimental validation requires understanding of internal behavior
- Scientific publication requires evidence trails

## 2. Metrics Model (Per Module)

### SEM-CSMF Metrics

**Location**: 

**Counters**:
- : Total intents processed
  - Labels:  (success, error, invalid)
  - Decision Phase: Semantic processing
- : Total invalid intents rejected
  - Labels:  (malformed, unsupported, ontology_error)
  - Decision Phase: Semantic validation

**Histograms**:
- : Semantic translation latency
  - Buckets: [10.0, 30.0, 50.0, 100.0, 200.0, 500.0, 1000.0, 2000.0, inf]
  - Decision Phase: Intent interpretation
- : Ontology reasoning latency
  - Buckets: [10.0, 30.0, 50.0, 100.0, 200.0, 500.0, 1000.0, 2000.0, inf]
  - Decision Phase: NEST generation

**Gauges**:
- : Number of intents currently being processed
  - Decision Phase: Semantic processing (in-progress indicator)

### ML-NSMF Metrics

**Location**: 

**Counters**:
- : Total ML prediction requests
  - Labels:  (eMBB, URLLC, mMTC),  (success, error)
  - Decision Phase: ML prediction
- : Total ML prediction errors
  - Labels: ,  (model_error, timeout, invalid_input)
  - Decision Phase: ML prediction (failure cases)

**Histograms**:
- : ML prediction latency
  - Labels: 
  - Buckets: [50.0, 100.0, 200.0, 400.0, 800.0, 1600.0, 3000.0, inf]
  - Decision Phase: ML inference

**Gauges**:
- : Average confidence score of ML predictions
  - Labels: 
  - Decision Phase: ML prediction (confidence indicator)
- : ML model version in use
  - Labels: 
  - Decision Phase: ML model metadata

### Decision Engine Metrics

**Location**: 

**Counters**:
- : Total intents processed
  - Labels:  (accepted, rejected, error)
  - Decision Phase: Decision pipeline
- : Total decisions accepted
  - Labels:  (sla_valid, capacity_available)
  - Decision Phase: Decision outcome (ACCEPT)
- : Total decisions rejected
  - Labels:  (sla_invalid, capacity_exceeded, timeout)
  - Decision Phase: Decision outcome (REJECT)

**Histograms**:
- : Total decision pipeline latency
  - Buckets: [100.0, 200.0, 300.0, 500.0, 1000.0, 2000.0, 5000.0, inf]
  - Decision Phase: End-to-end decision processing
- : SLA validation latency
  - Buckets: [50.0, 100.0, 200.0, 500.0, 1000.0, inf]
  - Decision Phase: SLA validation

**Gauges**:
- : Number of intents currently in pipeline
  - Decision Phase: Decision processing (in-progress indicator)

### BC-NSSMF Metrics

**Location**: 

**Counters**:
- : Total blockchain transactions
  - Labels:  (slice_contract, sla_contract),  (committed, failed)
  - Decision Phase: Blockchain registration (only for ACCEPT decisions)
- : Total blockchain transaction failures
  - Labels:  (contract_error, network_error, validation_error)
  - Decision Phase: Blockchain registration (failure cases)

**Histograms**:
- : Blockchain commit latency
  - Buckets: [100.0, 200.0, 500.0, 1000.0, 2000.0, 5000.0, 10000.0, inf]
  - Decision Phase: Blockchain transaction confirmation

**Gauges**:
- : Current blockchain block height
  - Decision Phase: Blockchain state
- : Number of pending transactions
  - Decision Phase: Blockchain queue state

### SLA-Agent Metrics

**Location**: 

**Counters**:
- : Total SLA contract compilation requests
  - Labels:  (slice_sla, network_sla),  (success, error)
  - Decision Phase: SLA lifecycle (post-decision)
- : Total SLA violations detected
  - Labels:  (critical, warning), 
  - Decision Phase: SLA compliance monitoring

**Histograms**:
- : SLA contract compilation latency
  - Buckets: [50.0, 100.0, 150.0, 200.0, 500.0, 1000.0, inf]
  - Decision Phase: SLA contract generation

**Gauges**:
- : Number of active SLA contracts
  - Decision Phase: SLA lifecycle (active contracts count)

### NASP Adapter Metrics

**Location**: NASP Adapter does not expose custom Prometheus metrics (uses FastAPI instrumentation)

**FastAPI Instrumentation** (if enabled):
- : Total HTTP requests
- : Request latency histogram
- : Error counter

**Decision Phase**: Metrics collection (used by Decision Engine and ML-NSMF)

### Portal Backend Metrics

**Location**: Portal Backend does not expose custom Prometheus metrics (uses FastAPI instrumentation)

**FastAPI Instrumentation** (if enabled):
- : Total HTTP requests
- : Request latency histogram
- : Error counter

**Decision Phase**: API orchestration (entry point for SLA submissions)

## 3. Tracing Architecture and Correlation

### OpenTelemetry Implementation

All TriSLA modules use OpenTelemetry for distributed tracing:

- **Tracer Provider**: Configured per module in 
- **OTLP Exporter**: Exports spans to OTLP collector at 
- **Span Processor**: BatchSpanProcessor for efficient export
- **Instrumentation**: FastAPIInstrumentor for automatic HTTP span creation

### Trace Structure

**End-to-End Trace Example** (SLA Submission):



### Correlation Identifiers

**intent_id**:
- **Generated by**: SEM-CSMF
- **Propagated via**: HTTP headers, Kafka message payloads, span attributes
- **Used by**: All modules to correlate operations
- **Span Attribute**:  or 

**decision_id**:
- **Generated by**: Decision Engine
- **Format**:  or UUID
- **Propagated via**: Kafka messages, HTTP responses, span attributes
- **Used by**: BC-NSSMF, SLA-Agent, Portal Backend
- **Span Attribute**:  or 

**sla_id**:
- **Generated by**: BC-NSSMF or Decision Engine
- **Propagated via**: HTTP responses, span attributes
- **Used by**: SLA-Agent, Portal Backend for lifecycle tracking
- **Span Attribute**:  or 

**nest_id**:
- **Generated by**: SEM-CSMF
- **Propagated via**: HTTP responses, span attributes
- **Used by**: Decision Engine, ML-NSMF
- **Span Attribute**:  or 

**trace_id**:
- **Generated by**: OpenTelemetry SDK (W3C TraceContext)
- **Propagated via**: HTTP headers (), gRPC metadata
- **Used by**: All modules for trace correlation
- **Format**: W3C TraceContext format

### Span Attributes

**Common Attributes** (all modules):
- : Module name (e.g., )
- : Module version (e.g., )
- : Deployment environment (e.g., )

**Decision-Specific Attributes**:
- : Intent identifier
- : Decision identifier
- : Decision outcome (ACCEPT, RENEG, REJECT)
- : Decision confidence score
- : NEST identifier
- : SLA identifier

**ML-Specific Attributes**:
- : ML risk score (0.0 to 1.0)
- : ML risk level (LOW, MEDIUM, HIGH)
- : ML confidence score
- : Boolean indicating fallback mode
- : Boolean indicating real metrics were collected

**Blockchain-Specific Attributes**:
- : Transaction hash
- : SLA identifier on-chain
- : Block number
- : Boolean indicating registration success

**NASP-Specific Attributes**:
- : Metrics source (nasp_real, nasp_mock)
- : NASP endpoint URL
- : Action domain (ran, transport, core)
- : Action type (activate, etc.)

### Trace Context Propagation

**HTTP Propagation**:
- **Format**: W3C TraceContext ( header)
- **Implementation**: OpenTelemetry propagators (TraceContextTextMapPropagator)
- **Automatic**: FastAPIInstrumentor automatically propagates trace context

**Kafka Propagation**:
- **Format**: Trace context in message headers
- **Implementation**: Manual propagation via message headers
- **Limitation**: Not all Kafka consumers propagate trace context (known gap)

**gRPC Propagation**:
- **Format**: gRPC metadata
- **Implementation**: OpenTelemetry gRPC instrumentation
- **Used by**: Decision Engine (legacy SEM-CSMF integration)

## 4. Logging Strategy and Identifiers

### Log Structure

All modules use structured logging with correlation identifiers:

**Log Format**:


**Example Logs**:


### Correlation in Logs

**Intent Submission** (Portal Backend):


**Decision Processing** (Decision Engine):


**Blockchain Registration** (BC-NSSMF):


**SLA Lifecycle** (SLA-Agent):


### Log Levels

- **DEBUG**: Detailed diagnostic information (not typically enabled in production)
- **INFO**: General informational messages (intent processing, decision outcomes)
- **WARNING**: Warning messages (degraded mode, fallback behavior)
- **ERROR**: Error messages (module failures, API errors)

### Log Aggregation

**Current State**: Logs are written to standard output, collected by Kubernetes logging system (if configured)

**Correlation**: Logs can be correlated with traces using  or with metrics using /

## 5. End-to-End Decision Traceability

### Trace Reconstruction

A complete decision trace can be reconstructed using:

1. **intent_id**: Query all logs, metrics, and traces with 
2. **decision_id**: Query all logs, metrics, and traces with 
3. **trace_id**: Query OpenTelemetry traces with 

### Decision Flow Traceability

**Phase 1: Intent Submission** (Portal Backend → SEM-CSMF)
- **Trace**:  span
- **Metrics**: 
- **Logs**: PAYLOAD_RECEBIDO, SERVICE_TYPE_EXTRAIDO
- **Correlation**:  generated by SEM-CSMF

**Phase 2: Semantic Processing** (SEM-CSMF)
- **Trace**:  span
- **Metrics**: , 
- **Logs**: Intent interpretation logs
- **Correlation**: ,  generated

**Phase 3: ML Prediction** (ML-NSMF)
- **Trace**:  span
- **Metrics**: , , 
- **Logs**: 🔍 FASE C2: Coletando metrics reais do Prometheus
- **Correlation**:  propagated

**Phase 4: Decision Making** (Decision Engine)
- **Trace**:  →  span
- **Metrics**: , , 
- **Logs**: 📥 SLA recebido, 💾 Decisão persistida, ✅ Decisão publicada no Kafka
- **Correlation**: ,  generated

**Phase 5: Blockchain Registration** (BC-NSSMF, only for ACCEPT)
- **Trace**:  span
- **Metrics**: , 
- **Logs**: Status SLA {sla_id} atualizado: tx_hash={tx_hash}
- **Correlation**: ,  generated

**Phase 6: SLA Lifecycle** (SLA-Agent)
- **Trace**:  span
- **Metrics**: , 
- **Logs**: [NSI] Creating NSI, [NSI-WATCH] NSI phase transition
- **Correlation**: , 

### Trace Query Examples

**Query by intent_id**:


**Query by decision_id**:


**Query OpenTelemetry traces**:


## 6. Dashboards and Experimental Evidence

### Prometheus Queries for Experimental Validation

**Decision Outcome Distribution**:


**End-to-End Latency**:


**ML Prediction Confidence**:


**Blockchain Transaction Rate**:


**SLA Violation Rate**:


### Grafana Dashboards

**Dashboard Categories** (configured in ):

1. **Category A - Availability**: Module health and availability metrics
2. **Category B - SLO/SLA-Aware**: SLA compliance and SLO metrics
3. **Category C - E2E Flow**: End-to-end decision flow metrics
4. **Category D - Capacity Saturation**: Resource utilization and capacity metrics

**Dashboard Purpose**: Dashboards visualize metrics for operational monitoring and experimental validation, but the **contribution** is the metrics themselves, not the dashboards.

### Experimental Evidence Collection

**Metrics for Experimental Validation**:
- Decision outcome distribution (ACCEPT/RENEG/REJECT ratios)
- End-to-end latency (p50, p95, p99)
- ML prediction accuracy (confidence scores, risk scores)
- Blockchain transaction success rate
- SLA violation rates

**Traces for Experimental Validation**:
- Complete decision flows (intent → decision → blockchain)
- Module interaction patterns
- Failure modes and recovery paths

**Logs for Experimental Validation**:
- Decision justifications
- Error messages and recovery actions
- Module state transitions

## 7. Failure Detection and Diagnosis

### Prometheus Alerting Rules

**Location**: 

**Category C - E2E Flow Alerts** ():
- : Interface I-01 (SEM-CSMF → ML-NSMF) failures
- : Interface I-02 (ML-NSMF → Decision Engine) failures
- : Interface I-03 (Decision Engine → BC-NSSMF) failures
- : No new intents processed for 5+ minutes
- : Intent processing rate below threshold

**Alert Evaluation**: Alerts are evaluated every 30 seconds (configurable via )

### Failure Detection via Metrics

**High Error Rate**:


**High Latency**:


**Blockchain Failures**:


### Diagnosis Workflow

1. **Detect Anomaly**: Alert fires or metric threshold exceeded
2. **Identify Module**: Check which module metric is anomalous
3. **Query Traces**: Use  or  to find related traces
4. **Check Logs**: Query logs for the same correlation identifiers
5. **Reconstruct Flow**: Use traces to reconstruct the decision flow
6. **Identify Root Cause**: Correlate metrics, traces, and logs to identify failure point

### Common Failure Patterns

**Pattern 1: SEM-CSMF Unavailable**
- **Symptom**:  increases
- **Trace**:  span has error status
- **Logs**: SEM-CSMF unavailable or connection errors
- **Diagnosis**: Check SEM-CSMF health endpoint, verify service discovery

**Pattern 2: ML-NSMF Timeout**
- **Symptom**:  increases
- **Trace**:  span has timeout error
- **Logs**: Timeout ao conectar com ML-NSMF
- **Diagnosis**: Check ML-NSMF health, verify network connectivity, check model inference time

**Pattern 3: Blockchain Transaction Failures**
- **Symptom**:  increases
- **Trace**:  span has error status
- **Logs**: Erro ao registrar SLA no blockchain
- **Diagnosis**: Check Besu node health, verify contract deployment, check transaction pool

## 8. Performance and Overhead Considerations

### Metrics Collection Overhead

**Prometheus Scraping**:
- **Interval**: 30 seconds (configurable via ServiceMonitor)
- **Timeout**: 10 seconds per scrape
- **Overhead**: Minimal (metrics are pre-computed, scraping is read-only)

**Metric Instrumentation**:
- **Counters**: Atomic increment (negligible overhead)
- **Histograms**: Time measurement + bucket update (microseconds)
- **Gauges**: Simple set operation (negligible overhead)

**Estimated Overhead**: < 1% CPU per module

### Tracing Overhead

**Span Creation**:
- **Overhead**: ~10-50 microseconds per span
- **Batch Export**: Spans are batched before export (reduces network overhead)

**OTLP Export**:
- **Endpoint**:  (gRPC)
- **Batch Size**: Configurable (default: 512 spans)
- **Export Interval**: Configurable (default: 5 seconds)

**Estimated Overhead**: < 2% CPU per module (with batching enabled)

### Logging Overhead

**Structured Logging**:
- **Overhead**: Minimal (string formatting)
- **I/O**: Asynchronous (buffered writes)

**Estimated Overhead**: < 0.5% CPU per module

### Total Observability Overhead

**Estimated Total**: < 3.5% CPU per module

**Mitigation Strategies**:
- Disable OpenTelemetry in development ()
- Reduce Prometheus scrape frequency for low-priority modules
- Use sampling for high-volume traces (if needed)

## 9. Known Issues and Lessons Learned

### Issue: Prometheus Queries Return Empty Results for Low-Frequency Metrics

**Symptom**:  queries return empty results for metrics in stable/low-churn clusters.

**Root Cause**:  requires at least 2 data points within the time window. In stable clusters, metrics may not change frequently enough.

**Resolution**:
1. Use  with longer windows for low-frequency signals
2. Prefer gauge-style ratios for CPU/memory/disk when churn is low
3. Ensure scrape interval (30s) and evaluation window (5m) are compatible

**Validation Evidence**: Metrics queries return valid results, dashboards display data correctly.

### Issue: Trace Spans Missing for Async Operations

**Symptom**: Kafka consumer operations do not appear in traces.

**Root Cause**: Trace context is not automatically propagated through Kafka messages.

**Resolution**:
1. Manually propagate trace context via Kafka message headers
2. Create explicit spans for Kafka consumer operations
3. Link spans using  from message headers

**Validation Evidence**: End-to-end traces include Kafka consumer spans, trace correlation works.

### Issue: Metrics Labels Inconsistent Across Modules

**Symptom**: Different modules use different label names for the same concept (e.g.,  vs ).

**Root Cause**: No standardized label naming convention initially.

**Resolution**:
1. Standardized label naming:  (not ),  (not ),  (not )
2. Updated all modules to use consistent labels
3. Documented label conventions in this guide

**Validation Evidence**: All modules use consistent label names, queries work across modules.

### Issue: OpenTelemetry Collector Unavailable

**Symptom**: Traces are not exported, spans are created but not visible in trace backend.

**Root Cause**: OTLP collector is not deployed or unreachable.

**Resolution**:
1. Verify OTLP collector is deployed: 
2. Verify endpoint configuration: 
3. Check network connectivity: 
4. Fallback: Disable OpenTelemetry () if collector unavailable

**Validation Evidence**: Traces are exported successfully, visible in trace backend (Jaeger/Tempo).

### Issue: ServiceMonitor Not Discovering Services

**Symptom**: Prometheus does not scrape TriSLA module metrics.

**Root Cause**: ServiceMonitor label selectors do not match service labels, or Prometheus Operator not installed.

**Resolution**:
1. Verify ServiceMonitor labels match service labels
2. Verify Prometheus Operator is installed: 
3. Check Prometheus configuration: 
4. Verify namespace selector matches TriSLA namespace

**Validation Evidence**: Prometheus discovers and scrapes all TriSLA services, metrics are available.

### Issue: High Cardinality Metrics

**Symptom**: Prometheus memory usage increases, queries become slow.

**Root Cause**: High-cardinality labels (e.g.,  in ) create many time series.

**Resolution**:
1. Limit high-cardinality labels (use  only when necessary)
2. Use recording rules to aggregate high-cardinality metrics
3. Consider removing high-cardinality labels for production

**Validation Evidence**: Prometheus memory usage is stable, queries perform well.

## 10. Reproducibility and Experimental Validation

### What Is Required to Reproduce Observability

1. **Prometheus**: Deployed and configured to scrape TriSLA services
2. **OpenTelemetry Collector**: Deployed and reachable at 
3. **ServiceMonitors**: Configured for all TriSLA modules (in )
4. **TriSLA Modules**: All modules deployed with observability enabled

### Metrics for Experimental Validation

**Decision Outcome Distribution**:
- Query: , 
- Purpose: Validate decision distribution matches experimental claims
- Reproducibility: Deterministic if input conditions are reproduced

**End-to-End Latency**:
- Query: 
- Purpose: Validate latency claims in experimental sections
- Reproducibility: Non-deterministic (depends on infrastructure state)

**ML Prediction Accuracy**:
- Query: 
- Purpose: Validate ML model performance claims
- Reproducibility: Deterministic if model and input data are reproduced

**Blockchain Transaction Success Rate**:
- Query: 
- Purpose: Validate blockchain integration reliability
- Reproducibility: Non-deterministic (depends on blockchain network state)

### Traces for Experimental Validation

**Complete Decision Flows**:
- Query traces by  or 
- Purpose: Validate end-to-end flow claims
- Reproducibility: Deterministic if input conditions are reproduced

**Module Interaction Patterns**:
- Query traces by  and time range
- Purpose: Validate module interaction claims
- Reproducibility: Deterministic if input conditions are reproduced

### Logs for Experimental Validation

**Decision Justifications**:
- Query logs by  or 
- Purpose: Validate decision reasoning claims
- Reproducibility: Deterministic if input conditions are reproduced

### Minimal Required Setup

1. **Prometheus**: Single Prometheus instance scraping TriSLA services
2. **OpenTelemetry Collector**: Single OTLP collector (optional, for traces)
3. **ServiceMonitors**: One ServiceMonitor per TriSLA module
4. **No Grafana Required**: Metrics can be queried directly via Prometheus API

### Mocking Strategies

**For Testing Without Real Infrastructure**:

1. **Mock Prometheus**: Deploy a simple HTTP server that returns mock Prometheus metrics
2. **Mock OTLP Collector**: Deploy a simple OTLP receiver that accepts spans (does not need to store them)
3. **Disable Observability**: Set  and disable Prometheus scraping for unit tests

### Deterministic Behavior Guarantees

- **Metric Values**: Deterministic if input conditions are reproduced
- **Trace Structure**: Deterministic if input conditions are reproduced
- **Log Content**: Deterministic if input conditions are reproduced
- **Correlation IDs**: Deterministic if input conditions are reproduced (intent_id, decision_id generation)

### Known Non-Reproducible Elements

1. **Infrastructure State**: Metrics depend on real-time infrastructure state (CPU, memory, network)
2. **Network Latency**: Trace durations vary with network conditions
3. **Blockchain State**: Blockchain metrics depend on network congestion and block production rate
4. **Timing**: Exact timestamps are non-deterministic, but relative timing is reproducible

### Validation Checklist for Reproduction

- [ ] Prometheus is scraping all TriSLA services
- [ ] All modules expose  endpoint
- [ ] ServiceMonitors are configured correctly
- [ ] OpenTelemetry collector is running (if traces enabled)
- [ ] Metrics queries return data
- [ ] Traces can be queried by  or 
- [ ] Logs include correlation identifiers
- [ ] End-to-end decision traces can be reconstructed
- [ ] Experimental claims can be validated using metrics/traces/logs

