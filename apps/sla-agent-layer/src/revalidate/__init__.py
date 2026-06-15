"""
SLA-Agent revalidate-telemetry module.

Implementa POST /api/v1/agent/revalidate-telemetry no SLA-Agent.
Lógica copiada 1:1 do Portal Backend (`routers/sla.py` + `telemetry/*`) durante a
FASE 2 da refatoração de responsabilidades (REFACTOR_TRISLA_RESPONSIBILITY_GUIDE.md).

NÃO alterar valores numéricos, PromQL ou semântica de campos sem replicar a mesma
mudança no backend até a FASE 7 (consolidação) — o objetivo desta fase é zero-diff
em `intent_id`, `execution_id_revalidation`, `telemetry_snapshot_atual`,
`drift_summary`, `revalidation_status`, `temporal_correlation`,
`metadata.remediation_evidence`.
"""

from .handler import revalidate_telemetry_handler  # noqa: F401
from .schemas import (  # noqa: F401
    SLARevalidateTelemetryRequest,
    SLARevalidateTelemetryResponse,
)
