# SLO Evaluation Model

> **TRACEABILITY_ONLY**
> **NOT OPERATIONAL SSOT**

This document preserves the research-level SLO evaluation abstraction. The operational runtime truth is documented in [`docs/modules/sla-agent-layer.md`](../../modules/sla-agent-layer.md) and implemented in `apps/sla-agent-layer/src/domain_compliance.py` plus `apps/sla-agent-layer/src/runtime_slo_evaluator.py`.

## Research objective

Evaluate whether an SLA remains compliant over time using observed metrics and SLO constraints.

```text
M = observed metrics
SLO = constraints
```

For each metric `m`, the research abstraction is:

```text
compliance(m) = TRUE if m satisfies the SLO threshold
```

A simplified compliance ratio may be expressed as:

```text
C = compliant metrics / total metrics
```

## Research states

The earlier research model used:

```text
OK
RISK
VIOLATED
```

These names do **not** represent the real runtime state set.

## Runtime state set

The frozen SLA-Agent runtime documents and exposes:

| Runtime state | Status |
|---------------|--------|
| `COMPLIANT` | ACTIVE |
| `WARNING` | ACTIVE |
| `AT_RISK` | ACTIVE |
| `VIOLATED` | ACTIVE |
| `INCOMPLETE` | NOT WIRED |

## Operational pointers

| Runtime concern | Operational SSOT |
|-----------------|------------------|
| Metric compliance | `compute_metric_compliance` |
| Domain compliance | `compute_all_domains_compliance` |
| Slice thresholds | `SLICE_THRESHOLDS` for URLLC, EMBB, MMTC |
| Explainability rows | `metric_explainability[]` |
| Runtime assurance | `evaluate_runtime_assurance` |

This research model must not be used to override implementation behavior, endpoint classification, or Phase 47 baseline documentation.
