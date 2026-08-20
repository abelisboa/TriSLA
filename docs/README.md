# TriSLA Documentation

This directory is the public index for TriSLA architecture, components,
interfaces, deployment, and observability documentation. The
[repository overview](../README.md) provides the current end-to-end summary
and takes precedence when older component material describes a different
runtime boundary.

## Architecture and interfaces

- [Repository architecture and runtime flow](../README.md#architecture)
- [Service interface contracts](modules/interfaces.md)
- [Telemetry integration](modules/telemetry.md)

## Components

- [SEM-CSMF](modules/sem-csmf.md)
- [ML-NSMF](modules/ml-nsmf.md)
- [Decision Engine](modules/decision-engine.md)
- [NASP Adapter](modules/nasp-adapter.md)
- [SLA-Agent](modules/sla-agent-layer.md)
- [Portal backend](modules/portal-backend.md)
- [Portal frontend](modules/portal-frontend.md)

The [application index](../apps/README.md) maps these services to their source
directories and identifies supporting components.

## Deployment and configuration

- [Helm chart index](../helm/README.md)
- [Main TriSLA chart](../helm/trisla/README.md)
- [Portal implementation and configuration](portal/README.md)
- [NASP Adapter documentation](nasp-adapter/README.md)

Environment-specific endpoints, credentials, and network configuration must
be supplied by the operator. See the repository overview for installation and
runtime validation commands.

## Observability

- [Observability guide](observability/OBSERVABILITY.md)
- [Observability component reference](modules/observability.md)
- [Telemetry component reference](modules/telemetry.md)

## Public dataset

The [dataset documentation](../datasets/README.md) records the available CSV
and Parquet artifacts, dimensions, schema version, and integrity hashes.

## Compatibility and historical material

The repository retains documentation for components and interfaces that are
still useful for compatibility or implementation history. These references do
not redefine the current core architecture:

- [BC-NSSMF compatibility documentation](modules/bc-nssmf.md)
- [Specialized BC-NSSMF reference](bc-nssmf/README.md)
- [Earlier UI dashboard source](../apps/ui-dashboard/)

## Scientific publication

Publication metadata pending.
