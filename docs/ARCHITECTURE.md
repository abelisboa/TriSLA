# TriSLA Architecture

## Overview

TriSLA implements a distributed microservices architecture for SLA management in 5G networks. The system is designed for high availability, scalability, and trustworthiness through blockchain-based enforcement.

## Conceptual Architecture



## Component Flow

### 1. Service Exposure (SEM-CSMF)
- Receives SLA requests from external clients
- Validates and authenticates requests
- Routes to ML-NSMF for prediction

### 2. Machine Learning (ML-NSMF)
- Predicts optimal network slice configurations
- Uses historical data and ML models
- Provides recommendations to Decision Engine

### 3. Decision Engine
- Makes final SLA decisions based on:
  - ML predictions
  - Current network state
  - Business policies
- Publishes events to Kafka

### 4. Message Broker (Kafka)
- Event streaming platform
- Enables asynchronous communication
- Ensures event ordering and durability

### 5. Blockchain (BC-NSSMF)
- Records SLA agreements immutably
- Provides trust and auditability
- Enables decentralized enforcement

### 6. SLA Agent Layer
- Monitors SLA compliance
- Triggers alerts on violations
- Reports metrics to observability stack

## Deployment Architecture

TriSLA is deployed using Kubernetes with Helm charts:

- **Namespace**: 
- **Image Registry**: 
- **Version**:  (frozen)

## Observability

The system includes comprehensive observability:

- **Prometheus**: Metrics collection
- **Grafana**: Visualization and dashboards
- **OpenTelemetry**: Distributed tracing
- **Alertmanager**: Alert management

## Network Integration

TriSLA integrates with 5G network infrastructure through:

- **NASP Adapter**: Network abstraction layer
- **RAN Interface**: Radio Access Network communication
- **Transport Interface**: Network transport layer
- **Core Interface**: 5G Core network functions

## Data Flow

1. **Request Flow**: Portal → SEM → ML → Decision → BC
2. **Event Flow**: Decision → Kafka → BC → SLA Agent
3. **Metrics Flow**: All components → Prometheus → Grafana

## Security

- JWT-based authentication
- gRPC for inter-service communication
- TLS for external interfaces
- Role-based access control

## References

For detailed deployment instructions, see:
- [Installation Guide](INSTALLATION.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Reproducibility Guide](REPRODUCIBILITY.md)
