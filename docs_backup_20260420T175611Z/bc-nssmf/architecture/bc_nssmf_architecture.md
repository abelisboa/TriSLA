# BC-NSSMF Architecture

## Components

- BCService (Web3 integration)
- Kafka Consumer (Decision Engine input)
- Smart Contract Executor
- Metrics Oracle
- REST API

---

## Data Flow

Decision Engine -> Kafka -> BC-NSSMF -> Smart Contract -> Blockchain

---

## Core Responsibilities

- Execute smart contract transactions
- Manage SLA lifecycle
- Interface with blockchain node (Besu)

