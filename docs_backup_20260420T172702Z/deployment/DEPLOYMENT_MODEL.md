# TriSLA v3.9.3 - Deployment Model

## Overview

This document defines the minimum deployment model required to reproduce the results from Chapter 6 of the TriSLA research.

## Logical Architecture



## Mandatory Components

### 1. Core Services (All Required)

- **SEM-CSMF**: Service Exposure Management
- **ML-NSMF**: Machine Learning Network Slice Management Function
- **Decision Engine**: Core decision-making component
- **BC-NSSMF**: Blockchain Network Slice Management Function
- **SLA-Agent Layer**: SLA monitoring and enforcement

### 2. Infrastructure (Required)

- **Kafka**: Message queue for inter-service communication

## Optional Components

- **Portal Backend/Frontend**: Web interface for management
- **UI Dashboard**: Monitoring dashboard
- **Traffic Exporter**: Network traffic metrics exporter
- **iperf3**: Network testing utility (for experiments only)

## Initialization Order

1. **Infrastructure First**
   - Kafka must be running and healthy before core services start

2. **Core Services (Parallel)**
   - SEM-CSMF
   - ML-NSMF
   - Decision Engine
   - BC-NSSMF
   - SLA-Agent Layer

3. **Optional Services (After Core)**
   - Portal Backend
   - Portal Frontend
   - UI Dashboard
   - Traffic Exporter

## Health Check Dependencies

### Kafka Health
- All core services depend on Kafka being ready
- Check: Kafka broker responding on port 9092

### Decision Engine Health
- ML-NSMF requires Decision Engine to be ready
- Check: Decision Engine API responding

### ML-NSMF Health
- BC-NSSMF may depend on ML-NSMF for predictions
- Check: ML-NSMF inference endpoint responding

## Minimum Viable Deployment

To reproduce Chapter 6 results, the minimum deployment includes:

1. All 5 core services (SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent)
2. Kafka
3. Network connectivity between services

Optional components enhance usability but are not required for core functionality.

## Deployment Verification

After deployment, verify:

- [ ] All mandatory pods are in Running state
- [ ] Kafka is accessible from all services
- [ ] Decision Engine responds to health checks
- [ ] ML-NSMF can perform inference
- [ ] Metrics are being collected (if observability is enabled)
- [ ] Events are flowing through Kafka

## Known Limitations

1. Observability stack (Prometheus/Grafana) may be in separate namespace
2. Hyperledger Besu is optional and may not be present
3. Some components may have environment-specific adapters (e.g., NASP Adapter)
