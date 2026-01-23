# TriSLA - Trustworthy Service Level Agreement Framework for 5G Networks

**Scientific Version**: v3.9.3 (Frozen)

## Overview

TriSLA is a comprehensive framework for managing Service Level Agreements (SLAs) in 5G network environments. It provides automated SLA negotiation, monitoring, and enforcement through a distributed architecture combining machine learning, blockchain, and microservices.

## Architecture

TriSLA follows a microservices-based architecture with the following core components:

- **SEM-CSMF**: Service Exposure and Management - Core Service Management Function
- **ML-NSMF**: Machine Learning - Network Slice Management Function
- **Decision Engine**: Intelligent decision-making for SLA optimization
- **BC-NSSMF**: Blockchain-based Network Slice Subnet Management Function
- **SLA-Agent**: Agent layer for SLA enforcement and monitoring
- **Portal**: Web-based management interface

## High-Level Flow



The system processes SLA requests through a pipeline:
1. Service Exposure (SEM) receives requests
2. Machine Learning (ML) predicts optimal configurations
3. Decision Engine makes final decisions
4. Events are published to Kafka
5. Blockchain (BC) records and enforces agreements

## Modules

-  - Service Exposure and Management
-  - Machine Learning NSMF
-  - Decision Engine
-  - Blockchain NSSMF
-  - SLA Agent Layer
-  - Portal Backend API
-  - Portal Frontend UI
-  - Besu Blockchain deployment

## Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Reproducibility](docs/REPRODUCIBILITY.md)
- [Architecture](docs/ARCHITECTURE.md)

## Version

This repository contains the **frozen scientific version v3.9.3** used for academic publication and reproducibility.

## License

See [LICENSE](LICENSE) file for details.

## Repository

- **GitHub**: https://github.com/abelisboa/TriSLA
- **Container Registry**: ghcr.io/abelisboa
