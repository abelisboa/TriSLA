# TriSLA Applications

This directory contains the application services and supporting components in
the TriSLA repository. The [repository overview](../README.md) describes the
end-to-end runtime flow, while the [documentation index](../docs/README.md)
links to component-specific references.

## Current core components

| Component | Directory | Role |
| --- | --- | --- |
| Portal backend / SLA Intake Gateway | [`portal-backend`](portal-backend/) | Coordinates SLA submission and the admission workflow. |
| Portal frontend | [`portal-frontend`](portal-frontend/) | Provides the browser-facing interface for SLA requests and status. |
| SEM-CSMF | [`sem-csmf`](sem-csmf/) | Interprets SLA intent and produces the semantic request representation. |
| ML-NSMF | [`ml-nsmf`](ml-nsmf/) | Evaluates multidomain feasibility and exposes prediction information. |
| Decision Engine | [`decision-engine`](decision-engine/) | Produces admission decisions from semantic and feasibility inputs. |
| NASP Adapter | [`nasp-adapter`](nasp-adapter/) | Applies policy, capacity, and provisioning checks at the infrastructure boundary. |
| SLA-Agent | [`sla-agent-layer`](sla-agent-layer/) | Supports runtime assurance, actuation, and lifecycle records. |
| Traffic Exporter | [`traffic-exporter`](traffic-exporter/) | Exposes traffic observations as Prometheus metrics. |

## Compatibility and supporting components

- [`bc-nssmf`](bc-nssmf/) and [`besu`](besu/) preserve the blockchain-backed
  compatibility path used by the current Portal workflow. They are not part of
  the current core architecture.
- [`ui-dashboard`](ui-dashboard/) preserves the earlier user interface.
- [`kafka`](kafka/) supports optional event transport; the primary admission
  path uses synchronous service APIs.
- The remaining directories contain shared code, network adapters, exporters,
  and testbed-oriented utilities used by specific deployments or validation
  workflows.
