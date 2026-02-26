# SLA-Agent Layer

The SLA-Agent Layer is a critical control-plane component of TriSLA that orchestrates lifecycle-level actions and monitoring after SLA admission decisions are made. It operates asynchronously, consuming decision events from the Decision Engine and coordinating platform actions across multiple network domains.

## Quick Links

- [Complete Guide](SLA_AGENT_COMPLETE_GUIDE.md) - Comprehensive technical documentation
- [Architecture Overview](../../ARCHITECTURE.md) - System-wide architecture
- [Deployment Guide](../../DEPLOYMENT.md) - Deployment instructions

## Purpose

The SLA-Agent Layer exists to:

1. **Consume Decision Events**: Receive and process admission decisions from the Decision Engine via Kafka topic `trisla-i05-actions`
2. **Coordinate Platform Actions**: Execute control-plane actions across federated network domains (RAN, Transport, Core)
3. **Monitor SLA Compliance**: Continuously evaluate Service Level Objectives (SLOs) against real-time metrics
4. **Emit Lifecycle Events**: Publish agent events and action results to Kafka topics `trisla-i06-agent-events` and `trisla-i07-agent-actions`
5. **Integrate with NASP**: Collect real-time infrastructure metrics via the NASP Adapter

## What It Does NOT Do

- **Does not make admission decisions** - Delegated to the Decision Engine
- **Does not process semantic intent** - Delegated to SEM-CSMF
- **Does not perform ML predictions** - Delegated to ML-NSMF
- **Does not register on-chain** - BC-NSSMF integration is handled separately (if enabled)
- **Does not operate in real-time** - Operates asynchronously via event-driven architecture

## Architecture Overview

The SLA-Agent Layer consists of:

- **ActionConsumer** (`src/kafka_consumer.py`): Kafka consumer for decision events (I-05)
- **EventProducer** (`src/kafka_producer.py`): Kafka producer for agent events (I-06, I-07)
- **AgentCoordinator** (`src/agent_coordinator.py`): Coordinates actions across federated domains
- **AgentRAN** (`src/agent_ran.py`): RAN domain agent
- **AgentTransport** (`src/agent_transport.py`): Transport domain agent
- **AgentCore** (`src/agent_core.py`): Core domain agent
- **SLOEvaluator** (`src/slo_evaluator.py`): Evaluates SLO compliance against metrics

## Key Features

- **Federated Agent Architecture**: Separate agents per network domain (RAN, Transport, Core)
- **Event-Driven Execution**: Asynchronous processing via Kafka
- **SLO Compliance Monitoring**: Continuous evaluation of metrics against configured SLOs
- **NASP Integration**: Real-time metric collection from platform infrastructure
- **Observability**: Prometheus metrics and OpenTelemetry traces

## Deployment

The SLA-Agent Layer is deployed via Helm chart `helm/trisla` under the `slaAgentLayer` section. See [Complete Guide](SLA_AGENT_COMPLETE_GUIDE.md) for detailed deployment and configuration instructions.

## Observability

- **Prometheus Metrics**: Exposed at `/metrics` endpoint
- **OpenTelemetry Traces**: Distributed tracing for event processing and action execution
- **Structured Logging**: JSON-formatted logs for lifecycle transitions

For detailed observability documentation, see [Complete Guide - Observability Section](SLA_AGENT_COMPLETE_GUIDE.md#observability-and-evidence).
