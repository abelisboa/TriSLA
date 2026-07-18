# BC-NSSMF Module

BC-NSSMF provides the blockchain-facing SLA persistence boundary. It accepts SLA registration and status requests, signs Besu transactions, waits for successful receipts, and exposes stored SLA state.

## Public contract

| Item | Value |
|---|---|
| Service | `trisla-bc-nssmf` |
| Port | `8083` |
| Health | `/health` |
| Readiness | `/health/ready` |
| Metrics | `/metrics` |
| Besu JSON-RPC | `trisla-besu:8545` |

The module supports degraded startup for diagnosis, but it does not report a blockchain commit unless the configured RPC, account, contract, and transaction receipt are valid.

## Main operations

- register SLA state;
- update SLA status;
- retrieve SLA state;
- validate contract-operation requests;
- export health and Prometheus metrics.

## References

- [BC-NSSMF documentation](../bc-nssmf/README.md)
- [Application source](../../apps/bc-nssmf/src/main.py)
- [Helm Deployment](../../helm/trisla/templates/deployment-bc-nssmf.yaml)
