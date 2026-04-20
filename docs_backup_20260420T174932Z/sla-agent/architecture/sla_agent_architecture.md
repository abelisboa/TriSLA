# SLA-Agent Layer Architecture

## Components

- ActionConsumer (I-05 Kafka consumer)
- AgentCoordinator
- AgentRAN
- AgentTransport
- AgentCore
- SLOEvaluator
- EventProducer (I-06/I-07)

## Data Flow

Decision Engine -> I-05 -> SLA-Agent -> SLO Evaluation -> I-06/I-07

## Responsibilities

- Execute post-admission actions
- Evaluate runtime SLO compliance
- Emit lifecycle and action events

