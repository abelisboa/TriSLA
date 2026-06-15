"""Compare KPI values across admission vs runtime snapshots."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


_KPI_PATHS = (
    ("prb_utilization", "ran", "prb_utilization", "%"),
    ("ran.latency_ms", "ran", "latency_ms", "ms"),
    ("transport.jitter_ms", "transport", "jitter_ms", "ms"),
    ("transport.packet_loss", "transport", "packet_loss", "%"),
    ("core.cpu", "core", "cpu_utilization", "%"),
)


def _pick(domain: Optional[Dict[str, Any]], key: str) -> Any:
    if not isinstance(domain, dict):
        return None
    return domain.get(key)


def build_telemetry_fidelity(
    admission_snapshot: Optional[Dict[str, Any]],
    runtime_snapshot: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    adm = admission_snapshot if isinstance(admission_snapshot, dict) else {}
    run = runtime_snapshot if isinstance(runtime_snapshot, dict) else {}
    rows: List[Dict[str, Any]] = []
    mismatches = 0
    for label, domain, field, unit in _KPI_PATHS:
        a = _pick(adm.get(domain) if isinstance(adm.get(domain), dict) else None, field)
        r = _pick(run.get(domain) if isinstance(run.get(domain), dict) else None, field)
        consistent = True
        if a is not None and r is not None:
            try:
                consistent = abs(float(a) - float(r)) < 0.01
            except (TypeError, ValueError):
                consistent = a == r
        if a is not None and r is not None and not consistent:
            mismatches += 1
        rows.append(
            {
                "kpi": label,
                "admission_value": a,
                "runtime_value": r,
                "unit": unit,
                "consistent": consistent,
            }
        )
    return {
        "kpi_rows": rows,
        "mismatch_count": mismatches,
        "consistent": mismatches == 0,
    }
