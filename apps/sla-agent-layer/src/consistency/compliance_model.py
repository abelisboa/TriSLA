"""Admission vs Runtime compliance separation."""
from __future__ import annotations

from typing import Any, Dict, Optional


def _normalize_pct(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    v = float(value)
    if v > 1.0:
        return round(v, 4)
    return round(v * 100.0, 2)


def split_compliance_fields(
    *,
    admission_compliance: Optional[float],
    runtime_compliance: Optional[float],
    admission_decision: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Returns explicit admission/runtime compliance (percent labels + raw fractions).
    Keeps sla_compliance as runtime alias for backward compatibility.
    """
    adm = admission_compliance
    run = runtime_compliance
    return {
        "admission_compliance": adm,
        "admission_compliance_percent": _normalize_pct(adm),
        "runtime_compliance": run,
        "runtime_compliance_percent": _normalize_pct(run),
        "admission_decision": admission_decision,
        # Deprecated generic label — document consumers should migrate
        "compliance_model_version": "2.0",
        "sla_compliance": run,
    }
