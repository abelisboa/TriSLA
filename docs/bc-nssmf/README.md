# BC-NSSMF

BC-NSSMF records SLA state through a Hyperledger Besu network. It exposes a FastAPI service for registration, status changes, lookup, and contract-operation requests.

## Runtime contract

| Item | Value |
|---|---|
| Service | `trisla-bc-nssmf` |
| Kubernetes type | `ClusterIP` |
| Port | `8083` |
| Liveness | `GET /health` |
| Readiness | `GET /health/ready` |
| Metrics | `GET /metrics` |
| Besu RPC | `http://trisla-besu:8545` |

`/health` reports whether blockchain support and RPC connectivity are available. `/health/ready` additionally checks RPC access and the configured signing account. Transaction endpoints return an error when the service is operating without blockchain connectivity.

## API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/register-sla` | Register SLA content and wait for a successful transaction receipt |
| `POST` | `/api/v1/update-sla-status` | Change the stored SLA status |
| `GET` | `/api/v1/get-sla/{sla_id}` | Read an SLA by numeric identifier |
| `POST` | `/api/v1/execute-contract` | Validate a contract-operation request and return its result |

The registration response includes the transaction hash, block number, SLA identifier, and commit status when the transaction succeeds.

## Documentation

- [Architecture](architecture/bc_nssmf_architecture.md)
- [REST interfaces](interfaces/interfaces.md)
- [SLA lifecycle](pipeline/sla_lifecycle.md)
- [Besu integration](blockchain/besu_integration.md)
- [Application entrypoint](../../apps/bc-nssmf/src/main.py)
