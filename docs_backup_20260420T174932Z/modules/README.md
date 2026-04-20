# TriSLA Modules (SSOT Index)

This folder documents runtime behavior from `apps/*/src` for all core services.

## Core modules

- [SEM-CSMF](./sem-csmf.md)
- [ML-NSMF](./ml-nsmf.md)
- [Decision Engine](./decision-engine.md)
- [NASP Adapter](./nasp-adapter.md)
- [SLA-Agent Layer](./sla-agent-layer.md)
- [BC-NSSMF](./bc-nssmf.md)
- [Portal Backend](./portal-backend.md)

## Auxiliary modules

- [Portal Frontend](./portal-frontend.md)
- [UI Dashboard](./ui-dashboard.md)
- [Kafka](./kafka.md)
- [Besu](./besu.md)
- [Network Exporter](./network-exporter.md)
- [Blockchain Exporter](./blockchain-exporter.md)
- [PRB Exporter](./prb-exporter.md)

## Canonical runtime pipeline

`SEM-CSMF -> ML-NSMF -> Decision Engine -> NASP Adapter -> BC-NSSMF -> SLA-Agent Layer`

## Documentation policy

- Endpoint contracts are documented exactly as implemented.
- Mathematical sections are derived from runtime behavior.
- Configuration-dependent branches are explicitly described as runtime policy parameters.

## Installation reference

For installation, refer to:

`docs/INSTALLATION_FINAL.md`
