# TriSLA - Trustworthy, Reasoned and Intelligent SLA-Aware

**Scientific Version**: v3.9.3 (Frozen)

## Overview

**TriSLA** (Trustworthy, Reasoned and Intelligent SLA-Aware) is a control-plane architecture focused on validation, decision-making, and automated execution of Service Level Agreements (SLAs) in Network Slicing environments for 5G/O-RAN networks, based on the integration of ontology, artificial intelligence, and smart contracts.

TriSLA addresses the heterogeneity of RAN, Transport, and Core domains, providing end-to-end automation in the slice lifecycle while prioritizing reliability, traceability, predictability, and transparency.

## What Problem Does TriSLA Solve?

TriSLA addresses the challenge of automated SLA validation, decision-making, and execution in 5G/O-RAN Network Slicing environments. It provides:

- **Semantic interpretation** of natural language intents using ontology
- **Intelligent decision-making** through Deep Learning and Explainable AI (XAI)
- **Automated lifecycle orchestration** from admission to execution and monitoring
- **Contractual formalization** via smart contracts on Distributed Ledger Technology (DLT)

## Architecture

TriSLA is composed exclusively of the following architectural elements:

### SEM-CSMF
- Semantic interpretation of natural language intents
- Ontology-based validation
- Generation of SLA-aware specifications

### ML-NSMF + Decision Engine
- Resource viability prediction
- Deep Learning models
- Explainable AI (XAI) support
- Decision process support (ACCEPT / REJECT / RENEG)

### BC-NSSMF
- Contractual clause formalization
- Execution via Smart Contracts
- Based on Distributed Ledger Technology (DLT)

### SLA-Agent Layer
- Slice lifecycle orchestration
- Integration between decision, execution, and monitoring
- End-to-end automation

## Scope and Limitations

### What TriSLA Is

- **Control-plane only**: Operates exclusively in the control plane
- **SLA-aware**: From semantic input to lifecycle execution
- **Domain-agnostic**: Addresses heterogeneity of RAN, Transport, and Core domains
- **5G/O-RAN focused**: Designed for 5G and O-RAN network environments
- **End-to-end automation**: Provides complete automation in slice lifecycle

### What TriSLA Is NOT

- **Direct RAN/Transport/Core configuration**: TriSLA does not directly configure radios, transport, or core. It delegates to the NASP Adapter and underlying platform.
- **Data-plane or user-plane**: No packet processing or user-plane functions.
- **Network orchestration platform replacement**: Does not replace network orchestration platforms.
- **End-user authentication**: No built-in IdP or RBAC for end-users; cluster-level access control applies.
- **Generic slicing platform**: Not a generic platform for network slicing.

## Documentation

- **[Installation Guide](docs/INSTALLATION.md)**: Conceptual prerequisites, infrastructure requirements, and environment validation
- **[Deployment Guide](docs/DEPLOYMENT.md)**: Step-by-step operational manual for deploying TriSLA
- **[Reproducibility](docs/REPRODUCIBILITY.md)**: Scientific reproducibility criteria and validation
- **[Architecture](docs/ARCHITECTURE.md)**: Detailed architectural documentation

## Version

This repository contains the **frozen scientific version v3.9.3** used for academic publication and reproducibility.

## License

See [LICENSE](LICENSE) file for details.

## Repository

- **GitHub**: https://github.com/abelisboa/TriSLA
- **Container Registry**: ghcr.io/abelisboa
