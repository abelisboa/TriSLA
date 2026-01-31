# TriSLA Blockchain Integration

## Overview

TriSLA uses Hyperledger Besu for immutable SLA registration, providing transparency and auditability.

## Technology

- **Blockchain**: Hyperledger Besu
- **Consensus**: QBFT (Quorum Byzantine Fault Tolerance)
- **Smart Contract**: Solidity

## Smart Contract

The SLA Registry contract stores:

```solidity
struct SLA {
    string slaId;
    string intentId;
    string serviceType;
    string decision;
    uint256 riskScore;
    uint256 timestamp;
    address registeredBy;
}
```

## BC-NSSMF

The BC-NSSMF component handles:

1. **SLA Registration**: Writes accepted SLAs to blockchain
2. **Transaction Signing**: Uses private key for authentication
3. **Event Emission**: Broadcasts SLA events
4. **Query Interface**: Retrieves SLA history

## Configuration

Environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| BESU_RPC_URL | Besu JSON-RPC endpoint | http://trisla-besu:8545 |
| CONTRACT_ADDRESS | Deployed contract address | (auto-detected) |
| PRIVATE_KEY | Account private key | (required) |

## Deployment

Besu runs in single-node QBFT mode:

```yaml
besu:
  enabled: true
  image:
    tag: v3.10.0
  persistence:
    enabled: true
    size: 10Gi
```

## Security

- Private keys stored in Kubernetes Secrets
- RPC endpoint internal only (ClusterIP)
- No public exposure of blockchain node
