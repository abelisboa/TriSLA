# TriSLA - SLA-Aware Architecture for 5G Network Slicing

**Version:** 3.10.0

## Overview

TriSLA is an SLA-aware architecture designed for automated network slice lifecycle management in 5G environments. It leverages Machine Learning for risk prediction, Explainable AI (XAI) for decision transparency, and Blockchain for immutable SLA registration.

## Architecture

![TriSLA Architecture](docs/architecture.png)

### Key Components

| Component | Description | Port |
|-----------|-------------|------|
| **Portal (UI Dashboard)** | Web interface for SLA creation and monitoring | 80 |
| **SEM-CSMF** | Service & Experience Management | 8080 |
| **ML-NSMF** | Machine Learning-based Network Slice Management | 8081 |
| **Decision Engine** | SLA admission control with XAI | 8082 |
| **BC-NSSMF** | Blockchain-based Network Slice Subnet Management | 8083 |
| **SLA-Agent Layer** | SLA enforcement and monitoring | 8084 |
| **NASP Adapter** | Network Slice Provider integration | 8085 |

### End-to-End Flow

1. **SLA Submission**: Tenant submits SLA request via Portal
2. **Intent Translation**: SEM-CSMF translates to network intent
3. **Risk Prediction**: ML-NSMF predicts SLA fulfillment risk
4. **Decision**: Decision Engine evaluates and generates XAI explanation
5. **Blockchain Registration**: BC-NSSMF registers SLA on Hyperledger Besu
6. **Slice Provisioning**: SLA-Agent delegates to NASP Adapter
7. **NASP Creation**: Network slice is instantiated in the 5G network

## Features

### Explainable AI (XAI)

Every SLA decision includes:
- **Risk Score**: Predicted probability of SLA violation
- **Confidence**: Model certainty in the prediction
- **Viability Score**: Overall feasibility assessment
- **Justification**: Human-readable explanation
- **Feature Importance**: Contributing factors

### Monitoring Dashboard

- Real-time SLA statistics
- Decision distribution charts (ACCEPT/REJECT/RENEG)
- Service type breakdown (eMBB, URLLC, mMTC)
- Expandable XAI details per SLA

### Blockchain Immutability

- Hyperledger Besu (QBFT consensus)
- Smart contract for SLA registration
- Transaction hash and block confirmation

## Quick Start

### Prerequisites

- Kubernetes cluster (1.26+)
- Helm 3.x
- Docker/Podman
- Free5GC or Open5GS (for NASP integration)

### Installation

```bash
# Clone repository
git clone https://github.com/abelisboa/trisla.git
cd trisla

# Install with Helm
helm install trisla ./helm/trisla -n trisla --create-namespace

# Access Portal
kubectl port-forward svc/trisla-ui-dashboard 8080:80 -n trisla
```

Open http://localhost:8080 in your browser.

## Project Structure

```
trisla/
├── apps/
│   ├── ui-dashboard/      # React frontend
│   ├── sem-csmf/          # Service Management
│   ├── ml-nsmf/           # ML predictions
│   ├── decision-engine/   # SLA decisions
│   ├── bc-nssmf/          # Blockchain
│   ├── sla-agent-layer/   # SLA enforcement
│   └── nasp-adapter/      # Network integration
├── helm/
│   └── trisla/            # Helm chart
└── docs/
    ├── architecture.md
    ├── portal.md
    └── blockchain.md
```

## Technology Stack

- **Frontend**: React, TypeScript, Material-UI, Recharts
- **Backend**: Python, FastAPI, Uvicorn
- **ML**: scikit-learn, XGBoost
- **Blockchain**: Hyperledger Besu, Solidity
- **Messaging**: Apache Kafka
- **Orchestration**: Kubernetes, Helm
- **Observability**: OpenTelemetry, Prometheus, Grafana

## API Documentation

Each service exposes Swagger/OpenAPI documentation:

- Portal Backend: `/docs`
- SEM-CSMF: `/docs`
- ML-NSMF: `/docs`
- Decision Engine: `/docs`
- BC-NSSMF: `/docs`
- SLA-Agent: `/docs`
- NASP Adapter: `/docs`

## License

Apache License 2.0

## Citation

If you use TriSLA in your research, please cite:

```bibtex
@inproceedings{trisla2026,
  title={TriSLA: An SLA-Aware Architecture for Explainable Network Slice Admission Control},
  author={Lisboa, Abel},
  year={2026}
}
```

## Contributors

- Abel Lisboa ([@abelisboa](https://github.com/abelisboa))

## Baseline v3.10.0

> **This is the scientific baseline v3.10.0, validated on a real NASP (5G/O-RAN-like) environment.**

This version serves as the experimental reference for the MSc dissertation and provides:

- Full end-to-end SLA lifecycle management
- XAI-based decision transparency
- Blockchain-backed SLA immutability
- Kafka-based observability and replay
- Reproducible deployment via Helm

### Citation

If you use TriSLA in your research, please cite:

```bibtex
@software{trisla2026,
  author = {Lisboa, Abel},
  title = {TriSLA: SLA-Aware Architecture for 5G Network Slicing},
  version = {3.10.0},
  year = {2026},
  url = {https://github.com/abelisboa/TriSLA}
}
```
