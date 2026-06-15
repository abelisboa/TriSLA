"""
Drift e missing-fields para revalidate-telemetry (sla-agent path).

Funções `_minimal_telemetry_drift` e `_snapshot_missing_fields` copiadas 1:1 de
apps/portal-backend/src/routers/sla.py — não alterar semântica sem replicar a
mesma mudança no backend até a FASE 7.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


def _minimal_telemetry_drift(reference: dict, current: dict) -> Dict[str, Any]:
    """P1: deltas numéricos null-safe entre snapshots (contract v2 / legacy keys)."""
    deltas: List[Dict[str, Any]] = []

    def pick_num(d: dict, *keys: str) -> Optional[float]:
        for k in keys:
            v = d.get(k)
            if v is not None:
                try:
                    return float(v)
                except (TypeError, ValueError):
                    continue
        return None

    def add_delta(path: str, ref_val: Optional[float], cur_val: Optional[float]) -> None:
        if ref_val is None and cur_val is None:
            return
        entry: Dict[str, Any] = {"path": path, "reference": ref_val, "current": cur_val}
        if ref_val is not None and cur_val is not None:
            entry["delta"] = cur_val - ref_val
        else:
            entry["delta"] = None
        deltas.append(entry)

    if not isinstance(reference, dict) or not isinstance(current, dict):
        return {"deltas": [], "fields_compared": 0, "error": "invalid_snapshot_shape"}

    ran_r = reference.get("ran") if isinstance(reference.get("ran"), dict) else {}
    ran_c = current.get("ran") if isinstance(current.get("ran"), dict) else {}
    tr_r = reference.get("transport") if isinstance(reference.get("transport"), dict) else {}
    tr_c = current.get("transport") if isinstance(current.get("transport"), dict) else {}
    co_r = reference.get("core") if isinstance(reference.get("core"), dict) else {}
    co_c = current.get("core") if isinstance(current.get("core"), dict) else {}

    add_delta("ran.prb_utilization", pick_num(ran_r, "prb_utilization"), pick_num(ran_c, "prb_utilization"))
    add_delta("ran.latency", pick_num(ran_r, "latency", "latency_ms"), pick_num(ran_c, "latency", "latency_ms"))
    add_delta("transport.rtt", pick_num(tr_r, "rtt", "rtt_ms"), pick_num(tr_c, "rtt", "rtt_ms"))
    add_delta("transport.jitter", pick_num(tr_r, "jitter", "jitter_ms"), pick_num(tr_c, "jitter", "jitter_ms"))
    add_delta("core.cpu", pick_num(co_r, "cpu", "cpu_utilization"), pick_num(co_c, "cpu", "cpu_utilization"))
    add_delta("core.memory", pick_num(co_r, "memory", "memory_bytes"), pick_num(co_c, "memory", "memory_bytes"))

    return {"deltas": deltas, "fields_compared": len(deltas)}


def _snapshot_missing_fields(snapshot: dict) -> List[str]:
    """Lista campos obrigatórios ausentes (valor None). Não inventa métricas."""
    missing: List[str] = []
    if not isinstance(snapshot, dict):
        return ["snapshot"]
    ran = snapshot.get("ran") if isinstance(snapshot.get("ran"), dict) else {}
    tr = snapshot.get("transport") if isinstance(snapshot.get("transport"), dict) else {}
    co = snapshot.get("core") if isinstance(snapshot.get("core"), dict) else {}

    if ran.get("prb_utilization") is None:
        missing.append("ran.prb_utilization")
    if ran.get("latency") is None and ran.get("latency_ms") is None:
        missing.append("ran.latency")

    if tr.get("rtt") is None and tr.get("rtt_ms") is None:
        missing.append("transport.rtt")
    if tr.get("jitter") is None and tr.get("jitter_ms") is None:
        missing.append("transport.jitter")

    cpu = co.get("cpu")
    if cpu is None:
        cpu = co.get("cpu_utilization")
    mem = co.get("memory")
    if mem is None:
        mem = co.get("memory_utilization")
    if cpu is None:
        missing.append("core.cpu")
    if mem is None:
        missing.append("core.memory")
    return missing
