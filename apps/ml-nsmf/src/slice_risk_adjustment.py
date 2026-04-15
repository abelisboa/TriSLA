"""
Ajuste semântico-operacional do risco por tipo de slice (URLLC / eMBB / mMTC).

Preserva o score bruto do modelo (`raw_risk`) e produz `slice_adjusted_risk_score`
com base em pesos por domínio e fatores observáveis nas métricas.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import math

# Pesos relativos por slice (latência, jitter, perda, throughput, banda, cpu, mem, confiabilidade, carga slices)
_SLICE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "URLLC": {
        "latency": 0.22,
        "jitter": 0.20,
        "packet_loss": 0.18,
        "throughput": 0.05,
        "network_bandwidth_available": 0.05,
        "cpu_utilization": 0.10,
        "memory_utilization": 0.10,
        "reliability": 0.05,
        "active_slices_count": 0.05,
    },
    "eMBB": {
        "latency": 0.10,
        "jitter": 0.05,
        "packet_loss": 0.06,
        "throughput": 0.22,
        "network_bandwidth_available": 0.22,
        "cpu_utilization": 0.12,
        "memory_utilization": 0.12,
        "reliability": 0.06,
        "active_slices_count": 0.05,
    },
    "mMTC": {
        "latency": 0.06,
        "jitter": 0.06,
        "packet_loss": 0.10,
        "throughput": 0.08,
        "network_bandwidth_available": 0.08,
        "cpu_utilization": 0.16,
        "memory_utilization": 0.16,
        "reliability": 0.18,
        "active_slices_count": 0.12,
    },
}

_DOMAIN_FEATURES = {
    "RAN": ("latency", "slice_type_encoded", "active_slices_count"),
    "Transport": ("jitter", "packet_loss", "throughput", "network_bandwidth_available"),
    "Core": ("cpu_utilization", "memory_utilization"),
}


def _norm_latency(lat: float) -> float:
    return max(0.0, min(1.0, float(lat) / 200.0))


def _norm_thr(throughput: float, bandwidth: float) -> float:
    """Baixo throughput relativo => maior contribuição de risco."""
    ref = max(bandwidth, throughput, 1e-6)
    return max(0.0, min(1.0, 1.0 - float(throughput) / ref))


def _norm_active(act: float) -> float:
    return max(0.0, min(1.0, math.log1p(max(act, 0.0)) / math.log1p(256.0)))


def _feature_risk_vector(metrics: Dict[str, Any]) -> Dict[str, float]:
    lat = float(metrics.get("latency", 0) or 0)
    thr = float(metrics.get("throughput", 0) or 0)
    rel = float(metrics.get("reliability", 0.99) or 0)
    jit = float(metrics.get("jitter", 0) or 0)
    pl = float(metrics.get("packet_loss", 0.001) or 0)
    cpu = float(metrics.get("cpu_utilization", 0.5) or 0)
    mem = float(metrics.get("memory_utilization", 0.5) or 0)
    bw = float(metrics.get("network_bandwidth_available", thr) or thr)
    act = float(metrics.get("active_slices_count", 1) or 1)

    return {
        "latency": _norm_latency(lat),
        "jitter": max(0.0, min(1.0, jit / 100.0)),
        "packet_loss": max(0.0, min(1.0, pl * 5.0)),
        "throughput": _norm_thr(thr, bw),
        "network_bandwidth_available": max(0.0, min(1.0, 1.0 - min(bw, 1e9) / max(bw + thr, 1.0))),
        "cpu_utilization": max(0.0, min(1.0, cpu)),
        "memory_utilization": max(0.0, min(1.0, mem)),
        "reliability": max(0.0, min(1.0, 1.0 - rel)),
        "active_slices_count": _norm_active(act),
    }


def _slice_key(slice_type: str) -> str:
    s = (slice_type or "eMBB").strip()
    up = s.upper()
    if up == "URLLC":
        return "URLLC"
    if up in ("EMBB", "EMB"):
        return "eMBB"
    if up == "MMTC":
        return "mMTC"
    return "eMBB"


def compute_slice_adjusted_risk(raw_risk: float, metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Combina risco bruto do modelo com pressão por domínio ponderada pelo slice.

    Retorna dict com scores, top fatores e domínio dominante (para XAI).
    """
    st_raw = metrics.get("slice_type")
    if st_raw is None or st_raw == "":
        enc = metrics.get("slice_type_encoded")
        if isinstance(enc, (int, float)):
            mp = {1: "URLLC", 2: "eMBB", 3: "mMTC"}
            st = mp.get(int(enc), "eMBB")
        else:
            st = "eMBB"
    else:
        st = _slice_key(str(st_raw))

    weights = _SLICE_WEIGHTS.get(st, _SLICE_WEIGHTS["eMBB"])
    fr = _feature_risk_vector(metrics)

    weighted = {k: fr[k] * weights.get(k, 0.0) for k in fr}
    domain_stress = sum(weighted.values())
    domain_stress = max(0.0, min(1.0, domain_stress))

    raw = max(0.0, min(1.0, float(raw_risk)))
    # Mistura: preserva o modelo mas inclina pela pressão observada por slice
    alpha = 0.42
    adjusted = max(0.0, min(1.0, (1.0 - alpha) * raw + alpha * domain_stress))

    # Top 3 fatores
    ranked: List[Tuple[str, float]] = sorted(
        ((k, v) for k, v in weighted.items() if v > 0),
        key=lambda x: x[1],
        reverse=True,
    )
    top3 = [{"factor": k, "weight": round(weights.get(k, 0.0), 4), "contribution": round(v, 6)} for k, v in ranked[:3]]

    dom_scores: Dict[str, float] = {}
    for dom, feats in _DOMAIN_FEATURES.items():
        dom_scores[dom] = sum(weighted.get(f, 0.0) for f in feats)
    dominant = max(dom_scores, key=lambda d: dom_scores[d]) if dom_scores else "Transport"

    return {
        "slice_type_resolved": st,
        "raw_risk_score": raw,
        "slice_adjusted_risk_score": adjusted,
        "domain_stress_score": round(domain_stress, 6),
        "top_factors": top3,
        "dominant_domain": dominant,
        "domain_contribution": {k: round(v, 6) for k, v in dom_scores.items()},
    }
