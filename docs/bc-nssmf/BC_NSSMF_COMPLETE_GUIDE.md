# BC-NSSMF Module Complete Guide

**Version:** 3.5.0  
**Date:** 2025-01-27  
**Module:** Blockchain-enabled Network Slice Subnet Management Function

---

## 📋 Table of Contents

1. [Overview](#overview)  
2. [Module Architecture](#module-architecture)  
3. [Smart Contracts](#smart-contracts)  
4. [Web3 Integration](#web3-integration)  
5. [REST and gRPC API](#rest-and-grpc-api)  
6. [Metrics Oracle](#metrics-oracle)  
7. [Integration with Other Modules](#integration-with-other-modules)  
8. [Interface I-04 (Kafka)](#interface-i-04-kafka)  
9. [Deployment and Configuration](#deployment-and-configuration)  
10. [Usage Examples](#usage-examples)  
11. [Troubleshooting](#troubleshooting)  

---

## 🎯 Overview

The **BC-NSSMF (Blockchain-enabled Network Slice Subnet Management Function)** is responsible for registering Service Level Agreements (SLAs) on-chain using a permissioned blockchain.  
Its purpose is to ensure **immutability**, **traceability**, and **deterministic execution** of contractual rules throughout the SLA lifecycle.

### Objectives

1. **On-Chain Registration:** Register SLAs approved by the Decision Engine on the blockchain  
2. **Status Update:** Update SLA status (ACTIVE, VIOLATED, TERMINATED)  
3. **Violation Registration:** Record SLA violations in an immutable manner  
4. **Auditing:** Provide full auditability through on-chain events  
5. **Enforcement:** Automatically execute contractual rules via smart contracts  

### Main Features

- **Blockchain:** Hyperledger Besu (permissioned Ethereum)  
- **Smart Contracts:** Solidity 0.8.20  
- **Web3 Client:** web3.py  
- **Confirmation Time:** < 5 seconds (local blockchain)  
- **Immutability:** All SLA events are permanently recorded on-chain  

---

## 🏗️ Module Architecture

### Directory Structure

apps/bc-nssmf/
├── src/
│ ├── main.py # FastAPI application
│ ├── service.py # BCService (Web3 integration)
│ ├── api_rest.py # REST API endpoints
│ ├── api_grpc_server.py # gRPC server (placeholder)
│ ├── models.py # Pydantic models
│ ├── config.py # Configuration
│ ├── oracle.py # MetricsOracle
│ ├── kafka_consumer.py # Kafka consumer (I-04)
│ ├── deploy_contracts.py # Smart contract deployment script
│ └── contracts/
│ ├── SLAContract.sol # Solidity smart contract
│ └── contract_address.json # Contract address and ABI
├── blockchain/
│ └── besu/
│ ├── docker-compose-besu.yaml # Besu Docker Compose
│ ├── genesis.json # Genesis block
│ └── data/ # Blockchain data
├── tests/
│ └── unit/ # Unit tests
├── Dockerfile
├── requirements.txt
└── README.md


### Main Components

1. **BCService** — Core Web3 integration service  
2. **SmartContractExecutor** — Smart contract execution handler  
3. **MetricsOracle** — Retrieves real-time metrics from NASP  
4. **DecisionConsumer** — Kafka consumer for decisions (Interface I-04)  
5. **SLAContract** — Solidity smart contract  

### Data Flow

Decision Engine (Kafka I-04)
│
▼
Kafka Consumer (BC-NSSMF)
│
▼
BCService
│
▼
SLA Smart Contract (Besu)
│
▼
On-Chain Events (SLARequested, SLAUpdated)


---

## 📜 Smart Contracts

### SLAContract.sol

**Location:** `apps/bc-nssmf/src/contracts/SLAContract.sol`  
**Solidity Version:** 0.8.20  

#### Structures

```solidity
enum SLAStatus {
    REQUESTED,
    APPROVED,
    REJECTED,
    ACTIVE,
    COMPLETED
}

struct SLO {
    string name;
    uint256 value;
    uint256 threshold;
}

struct SLA {
    uint256 id;
    string customer;
    string serviceName;
    bytes32 slaHash;
    SLAStatus status;
    SLO[] slos;
    uint256 createdAt;
    uint256 updatedAt;
}
Main Functions
registerSLA()

Registers a new SLA on-chain

Parameters: customer, serviceName, slaHash, slos[]

Returns: slaId (uint256)

Emits: SLARequested

updateSLAStatus()

Updates the SLA status

Parameters: slaId, newStatus

Emits: SLAUpdated

getSLA()

Retrieves SLA data

Parameters: slaId

Returns: customer, serviceName, status, createdAt, updatedAt

Events
solidity

event SLARequested(uint256 indexed slaId, string customer, string serviceName);
event SLAUpdated(uint256 indexed slaId, SLAStatus status);
event SLACompleted(uint256 indexed slaId);
🔗 Web3 Integration
BCService
File: apps/bc-nssmf/src/service.py
Class: BCService

Initialization

from service import BCService
service = BCService()
Execution Flow
Connects to the Besu RPC via Web3.HTTPProvider

Loads the smart contract ABI and address

Instantiates the contract object

Selects the default blockchain account

🌐 REST and gRPC API
REST API
File: apps/bc-nssmf/src/api_rest.py

POST /bc/register — Register an SLA on-chain

POST /bc/update — Update SLA status

GET /bc/{sla_id} — Retrieve SLA details

gRPC API (Placeholder)
File: apps/bc-nssmf/src/api_grpc_server.py
Status: Functional placeholder (minimal structure)

Note: Full gRPC implementation is defined in interfaces I-01 to I-07.

🔮 Metrics Oracle
File: apps/bc-nssmf/src/oracle.py

The Metrics Oracle retrieves real-time metrics from NASP and validates them against SLA thresholds before smart contract enforcement.

🔌 Integration with Other Modules
Decision Engine (I-04): Kafka consumer for ACCEPT/REJECT decisions

SLO Reporter: REST-based SLA violation reporting

NASP Adapter: Real-time metrics provider

🚀 Deployment and Configuration

cd apps/bc-nssmf/blockchain/besu
docker-compose -f docker-compose-besu.yaml up -d


cd apps/bc-nssmf
python src/deploy_contracts.py
📊 Observability
Prometheus metrics for transactions, latency, gas usage

OpenTelemetry traces for SLA lifecycle operations

🎯 Conclusion
The BC-NSSMF ensures immutable, auditable, and automated on-chain SLA management, fully integrated with the TriSLA architecture.

End of Guide
