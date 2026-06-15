"""NASP reachability aggregation (Sprint 5N2 — presentation layer only)."""
from __future__ import annotations

from typing import Any, Dict, List

NASP_MODULE_KEYS: List[str] = [
    "sem_csmf",
    "ml_nsmf",
    "decision",
    "bc_nssmf",
    "sla_agent",
]


def _module_reachable(probe: Any) -> bool:
    if not isinstance(probe, dict):
        return False
    if probe.get("reachable") is True:
        return True
    code = probe.get("status_code")
    if code == 200 or code == "200":
        return True
    return False


def aggregate_nasp_reachability(diagnostics: Dict[str, Any]) -> Dict[str, int]:
    """Derive operator-facing reachability counts from /nasp/diagnostics probes."""
    total = len(NASP_MODULE_KEYS)
    reachable = sum(
        1 for key in NASP_MODULE_KEYS if _module_reachable(diagnostics.get(key))
    )
    percent = round(100 * reachable / total) if total else 0
    return {
        "reachable_modules": reachable,
        "total_modules": total,
        "reachability_percent": percent,
    }
