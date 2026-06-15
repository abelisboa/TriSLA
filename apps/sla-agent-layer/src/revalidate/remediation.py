"""
Remediation evidence P2 (sla-agent path).

`_build_remediation_evidence_p2`, `_p2_env_float`, `_domain_from_drift_path`
copiados 1:1 de apps/portal-backend/src/routers/sla.py.

Não alterar limiares ou textos sem replicar a mesma mudança no backend até a FASE 7.
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

from .drift import _snapshot_missing_fields


def _p2_env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


def _domain_from_drift_path(path: str) -> str:
    if path.startswith("ran."):
        return "ran"
    if path.startswith("transport."):
        return "transport"
    if path.startswith("core."):
        return "core"
    return "unknown"


def _build_remediation_evidence_p2(
    *,
    drift_summary: Dict[str, Any],
    reference: Optional[Dict[str, Any]],
    current: Dict[str, Any],
    revalidation_status: str,
) -> Dict[str, Any]:
    """
    P2: evidência declarativa apenas — sem execução automática, orchestration ou callbacks.
    Usa drift_summary, limiares mínimos (env) e snapshots ref/atual.
    """
    th_prb = _p2_env_float("TRISLA_P2_PRB_DELTA_THRESHOLD", 5.0)
    th_lat = _p2_env_float("TRISLA_P2_LATENCY_MS_DELTA_THRESHOLD", 2.0)
    th_rtt = _p2_env_float("TRISLA_P2_RTT_MS_DELTA_THRESHOLD", 1.0)
    th_jit = _p2_env_float("TRISLA_P2_JITTER_MS_DELTA_THRESHOLD", 1.0)
    th_cpu = _p2_env_float("TRISLA_P2_CPU_DELTA_THRESHOLD", 5.0)
    th_mem_rel = _p2_env_float("TRISLA_P2_MEMORY_RELATIVE_THRESHOLD", 0.05)

    path_abs_thresholds = {
        "ran.prb_utilization": th_prb,
        "ran.latency": th_lat,
        "transport.rtt": th_rtt,
        "transport.jitter": th_jit,
        "core.cpu": th_cpu,
    }

    affected: set[str] = set()
    breach_paths: list[str] = []

    compared = bool(drift_summary.get("compared"))
    if not compared:
        if revalidation_status == "INCOMPLETE":
            for g in _snapshot_missing_fields(current):
                dom = g.split(".", 1)[0]
                if dom in ("ran", "transport", "core"):
                    affected.add(dom)
            return {
                "recommendation": (
                    "Telemetria atual incompleta e sem snapshot de referência; "
                    "não há correlação de drift numérica."
                ),
                "severity": "MEDIUM",
                "affected_domains": sorted(affected),
                "suggested_action": (
                    "Completar exportação Prometheus para o snapshot atual e "
                    "reenviar revalidate-telemetry com reference_telemetry_snapshot."
                ),
                "revalidation_required": True,
            }
        return {
            "recommendation": (
                "Nenhuma comparação de drift: reference_telemetry_snapshot não foi enviado."
            ),
            "severity": "INFO",
            "affected_domains": [],
            "suggested_action": (
                "Opcional: incluir reference_telemetry_snapshot (ex.: metadata.telemetry_snapshot "
                "do submit) para gerar deltas e avaliação de remediação declarativa."
            ),
            "revalidation_required": False,
        }

    for d in drift_summary.get("deltas") or []:
        if not isinstance(d, dict):
            continue
        path = str(d.get("path") or "")
        delta = d.get("delta")
        ref_v = d.get("reference")
        cur_v = d.get("current")

        if path == "core.memory":
            if (
                ref_v is not None
                and cur_v is not None
                and isinstance(ref_v, (int, float))
                and isinstance(cur_v, (int, float))
            ):
                rv = float(ref_v)
                cv = float(cur_v)
                base = max(abs(rv), 1e-9)
                if abs(cv - rv) / base > th_mem_rel:
                    affected.add("core")
                    breach_paths.append(path)
            continue

        if isinstance(delta, (int, float)):
            lim = path_abs_thresholds.get(path)
            if lim is not None and abs(float(delta)) > lim:
                dom = _domain_from_drift_path(path)
                if dom != "unknown":
                    affected.add(dom)
                breach_paths.append(path)

    if revalidation_status == "INCOMPLETE":
        for g in _snapshot_missing_fields(current):
            dom = g.split(".", 1)[0]
            if dom in ("ran", "transport", "core"):
                affected.add(dom)

    affected_sorted = sorted(affected)

    if not affected_sorted:
        return {
            "recommendation": (
                "Nenhum desvio acima dos limiares mínimos configurados; "
                "telemetria atual dentro da banda em relação à referência."
            ),
            "severity": "INFO",
            "affected_domains": [],
            "suggested_action": (
                "Nenhuma ação declarativa obrigatória; manter observabilidade conforme política de SLA."
            ),
            "revalidation_required": False,
        }

    if len(affected_sorted) > 1 or len(breach_paths) > 2:
        severity = "HIGH"
    else:
        severity = "MEDIUM"

    breach_txt = ", ".join(breach_paths) if breach_paths else ", ".join(affected_sorted)
    return {
        "recommendation": (
            f"Desvio temporal acima dos limiares mínimos nos caminhos: {breach_txt}."
        ),
        "severity": severity,
        "affected_domains": affected_sorted,
        "suggested_action": (
            "Revisar domínios listados e a política de slice no plano de controle; "
            "após correções operacionais, chamar novamente revalidate-telemetry "
            "(sem execução automática neste endpoint)."
        ),
        "revalidation_required": True,
    }
