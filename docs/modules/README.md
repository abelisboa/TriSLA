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

## Canonical runtime pipeline

`SEM-CSMF -> ML-NSMF -> Decision Engine -> NASP Adapter -> BC-NSSMF -> SLA-Agent Layer`

## Documentation policy

- Endpoint contracts are documented exactly as implemented.
- Mathematical sections are derived from runtime behavior.
- Configuration-dependent branches are explicitly described as runtime policy parameters.
