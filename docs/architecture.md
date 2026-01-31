# TriSLA Architecture

## System Overview

TriSLA implements a microservices architecture for SLA-aware network slice management.

## Components

### Portal (UI Dashboard)
- **Technology**: React, TypeScript, Material-UI
- **Function**: User interface for SLA submission and monitoring
- **Features**: XAI visualization, SLA dashboard, real-time metrics

### SEM-CSMF (Service & Experience Management)
- **Technology**: Python, FastAPI
- **Function**: Translates user intents into network slice requirements
- **Integration**: Receives requests from Portal, forwards to ML-NSMF

### ML-NSMF (Machine Learning Network Slice Management)
- **Technology**: Python, scikit-learn, XGBoost
- **Function**: Predicts SLA fulfillment risk using ML models
- **Output**: Risk score, confidence, feature importance

### Decision Engine
- **Technology**: Python, FastAPI
- **Function**: Orchestrates SLA admission decision
- **Features**: XAI generation, multi-domain evaluation, Kafka events

### BC-NSSMF (Blockchain Network Slice Subnet Management)
- **Technology**: Python, Web3.py, Solidity
- **Function**: Registers accepted SLAs on blockchain
- **Blockchain**: Hyperledger Besu (QBFT consensus)

### SLA-Agent Layer
- **Technology**: Python, FastAPI
- **Function**: Enforces SLA constraints, monitors compliance
- **Integration**: Connects to NASP Adapter for slice operations

### NASP Adapter
- **Technology**: Python, FastAPI
- **Function**: Abstracts network slice provider interface
- **Integration**: Communicates with Free5GC/Open5GS

## Data Flow

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Portal  │───►│ SEM-CSMF │───►│ ML-NSMF  │───►│ Decision │
│          │    │          │    │          │    │  Engine  │
└──────────┘    └──────────┘    └──────────┘    └────┬─────┘
                                                      │
                    ┌─────────────────────────────────┘
                    ▼
┌──────────┐    ┌──────────┐    ┌──────────┐
│ BC-NSSMF │◄───┤SLA-Agent │◄───┤   NASP   │
│ (Besu)   │    │  Layer   │    │ Adapter  │
└──────────┘    └──────────┘    └──────────┘
```

## Communication Patterns

| Pattern | Protocol | Use Case |
|---------|----------|----------|
| Synchronous | HTTP/REST | SLA submission, status queries |
| Asynchronous | Kafka | Decision events, observability |
| Blockchain | JSON-RPC | SLA registration |

## Deployment

- **Orchestration**: Kubernetes
- **Packaging**: Helm
- **Registry**: GitHub Container Registry (ghcr.io)
