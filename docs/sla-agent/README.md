# SLA-Agent Layer - Documentation Index

**Operational reference:** [`docs/modules/sla-agent-layer.md`](../modules/sla-agent-layer.md)

This directory is a navigation hub for specialized SLA-Agent references only. Runtime role, REST catalog, hot paths, telemetry truth, compliance, explainability, assurance, governance boundaries, integrations, observability, and persistence are documented in the operational module doc, not duplicated here.

## Contents

| Document | Purpose |
|----------|---------|
| [`interfaces/interfaces.md`](interfaces/interfaces.md) | Primary Portal -> SLA-Agent revalidation interface and endpoint classifications |
| [`architecture/sla_agent_architecture.md`](architecture/sla_agent_architecture.md) | Minimal architecture pointer to the canonical operational entry point |
| [`model/slo_evaluation_model.md`](model/slo_evaluation_model.md) | Research-only SLO model; not the operational SSOT |
| [`pipeline/lifecycle_execution.md`](pipeline/lifecycle_execution.md) | Runtime pipeline pointer and hot-path summary |
| [`observability/observability.md`](observability/observability.md) | Observability notes for metrics and tracing |

## External SSOT (read-only)

- `apps/sla-agent-layer/src/` - implementation
- `apps/sla-agent-layer/src/main.py` - REST endpoint registration
- `apps/sla-agent-layer/src/revalidate/` - telemetry reassessment implementation
- `apps/sla-agent-layer/src/domain_compliance.py` - compliance and explainability rows
- `apps/sla-agent-layer/src/runtime_slo_evaluator.py` - runtime assurance evaluation
- `baseline-registry/OPERATIONAL_BASELINE_REGISTRY.json` - operational digest
