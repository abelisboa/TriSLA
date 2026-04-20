# NASP Adapter Module

## Overview

The NASP Adapter is TriSLA's integration boundary with real infrastructure domains. It collects and normalizes multi-domain metrics and executes platform actions through a stable REST interface.

## Role in TriSLA

- Receives infrastructure-related requests from control modules
- Exposes normalized RAN/Transport/Core metrics
- Executes platform-level actions and returns orchestration results

## Formal View

Input space:

`u_nasp = (a, nsi_payload, gate_state, capacity_state)`

Output space:

`y_nasp = (orchestration_result, normalized_metrics, metadata)`

Normalization:

`m_norm = (m - min) / (max - min)`

## Responsibilities

- Metric collection from heterogeneous sources
- Cross-domain metric normalization
- NSI-related action execution with safety checks
- Runtime evidence generation for downstream lifecycle/audit modules

## Boundaries

The module does not perform:

- SLA admission decisions (Decision Engine)
- semantic interpretation (SEM-CSMF)
- risk prediction (ML-NSMF)

## References

- `docs/nasp-adapter/README.md`
- `docs/nasp-adapter/model/metric_normalization_model.md`
- `docs/nasp-adapter/interfaces/interfaces.md`
- `docs/nasp-adapter/integration/nasp_integration.md`
- `docs/nasp-adapter/observability/observability.md`
