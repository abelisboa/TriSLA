# TriSLA - Triangulated Service Level Agreement Platform

**Scientific Version**: v3.9.3 (Frozen)

## Overview

**TriSLA** (Triangulated Service Level Agreement Platform) is an SLA-aware control-plane architecture based on Artificial Intelligence, Ontology, and Smart Contracts for SLA assurance in 5G and O-RAN networks.

TriSLA provides automated SLA negotiation, monitoring, and enforcement through a distributed microservices architecture that combines:

- **Artificial Intelligence**: Machine learning models for risk prediction and decision optimization
- **Ontology**: Semantic processing and intent normalization for SLA validation
- **Smart Contracts**: Blockchain-based governance for on-chain SLA lifecycle management

## Architecture

TriSLA follows a microservices-based architecture deployed on Kubernetes with the following core components:

- **SEM-CSMF**: Semantic Core Service Management Function - intent normalization and ontology-based validation
- **ML-NSMF**: Machine Learning Network Slice Management Function - risk prediction and confidence scoring
- **Decision Engine**: Orchestrates semantic validation and ML inference to produce SLA admission decisions
- **BC-NSSMF**: Blockchain-based Network Slice Subnet Management Function - on-chain SLA registration and governance
- **SLA-Agent**: Event-driven agent layer for SLA enforcement, lifecycle actions, and SLO monitoring
- **NASP Adapter**: Platform abstraction layer for integration with external RAN, Transport, and Core platforms
- **Portal**: Web-based management interface for SLA submission and status monitoring

## High-Level Flow

The system processes SLA requests through an event-driven pipeline:

1. **SLA Submission**: Client submits SLA request via Portal or API
2. **Semantic Validation**: SEM-CSMF validates intent against ontology and normalizes the request
3. **ML Inference**: ML-NSMF predicts compliance risk and provides confidence scores
4. **Decision Making**: Decision Engine orchestrates validation and inference to produce ACCEPT/REJECT/RENEG decision
5. **Event Publishing**: Decision events are published to Kafka (event backbone)
6. **Lifecycle Actions**: SLA-Agent consumes events and executes post-admission actions
7. **Blockchain Recording**: BC-NSSMF (optional) records SLA lifecycle on-chain via smart contracts

## Documentation

- **[Installation Guide](docs/INSTALLATION.md)**: Conceptual prerequisites, infrastructure requirements, and environment validation
- **[Deployment Guide](docs/deployment/DEPLOYMENT.md)**: Step-by-step operational manual for deploying TriSLA
- **[Reproducibility](docs/REPRODUCIBILITY.md)**: Scientific reproducibility criteria and validation
- **[Architecture](docs/ARCHITECTURE.md)**: Detailed architectural documentation

## Version

This repository contains the **frozen scientific version v3.9.3** used for academic publication and reproducibility.

## License

See [LICENSE](LICENSE) file for details.

## Repository

- **GitHub**: https://github.com/abelisboa/TriSLA
- **Container Registry**: ghcr.io/abelisboa
