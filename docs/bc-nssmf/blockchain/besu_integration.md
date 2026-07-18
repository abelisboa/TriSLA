# Besu Integration

BC-NSSMF uses Hyperledger Besu through HTTP JSON-RPC. The deployed network reports chain ID `1337`.

## Network endpoints

| Endpoint | Port | Use |
|---|---:|---|
| JSON-RPC HTTP | `8545` | Web3 requests from BC-NSSMF |
| JSON-RPC WebSocket | `8546` | WebSocket clients |
| Peer traffic | `30303` | Besu node communication |

The Kubernetes Service is `ClusterIP`; these ports are not published as NodePorts by the main chart.

## Transaction path

1. BC-NSSMF loads the contract address and ABI.
2. The wallet module loads the signing key from `BC_PRIVATE_KEY`.
3. The sender obtains the pending nonce and builds a transaction for chain ID `1337`.
4. The transaction is signed locally and sent with `eth_sendRawTransaction`.
5. BC-NSSMF waits for a bounded transaction receipt and accepts only receipt status `1`.

The sender serializes transactions per account when its queue is enabled and retries recognized nonce or replacement-price errors with an updated gas price.

## Deployment resources

The Besu Deployment mounts its genesis configuration, validator key, and persistent data volume. TCP readiness and liveness probes check port `8545`.

Never place a signing key directly in a values file or command example. Create a pre-existing Kubernetes Secret containing the `BC_PRIVATE_KEY` value, then set `bcNssmf.wallet.existingSecret` and `bcNssmf.wallet.key` to its name and data key.

## References

- [Transaction sender](../../../apps/bc-nssmf/src/blockchain/tx_sender.py)
- [Besu Deployment template](../../../helm/trisla/templates/deployment-besu.yaml)
- [Besu Service template](../../../helm/trisla/templates/service-besu.yaml)
