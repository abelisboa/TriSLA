# BC-NSSMF Architecture

## Components

```text
Portal Backend or platform service
                │ HTTP :8083
                ▼
          BC-NSSMF FastAPI
                │ Web3 JSON-RPC
                ▼
          Hyperledger Besu :8545
                │
                ▼
          SLAContract state
```

The FastAPI layer validates requests, normalizes supported SLA payloads, and maps service errors to HTTP responses. `BCService` loads the deployed contract description, creates Web3 calls, signs transactions with the configured account, and requires a successful receipt before reporting a commit.

## Failure behavior

The process can start when blockchain support is disabled or the RPC endpoint is unavailable. In that state, `/health` reports `degraded`, readiness fails, and transaction-dependent endpoints return service errors. This keeps diagnosis available without reporting a successful blockchain operation.

## Deployment

The Helm chart deploys one `ClusterIP` service on port `8083`. The container and service use the same port. Liveness uses `/health`; readiness uses `/health/ready`.

The Deployment mounts:

- a Kubernetes Secret containing the signing key;
- a ConfigMap containing the deployed contract address and ABI.

Besu is a separate chart workload with JSON-RPC on `8545`, WebSocket RPC on `8546`, peer traffic on `30303`, and persistent storage.

## References

- [BC-NSSMF entrypoint](../../../apps/bc-nssmf/src/main.py)
- [Blockchain service](../../../apps/bc-nssmf/src/service.py)
- [BC-NSSMF Helm Deployment](../../../helm/trisla/templates/deployment-bc-nssmf.yaml)
- [Besu Helm Deployment](../../../helm/trisla/templates/deployment-besu.yaml)
