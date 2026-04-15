"""
Limiares dinâmicos por tipo de slice para o Decision Engine.

Usa `slice_adjusted_risk_score` quando disponível; caso contrário, recai no risco bruto.
Valores iniciais calibrados a partir da fronteira global (~0.55 / ~0.75), com folgas por slice.
"""

from __future__ import annotations

from typing import Dict, Tuple

# accept: risco estritamente abaixo deste valor => ACCEPT
# renegotiate: risco >= accept e < renegotiate_upper => RENEGOTIATE (upper é exclusivo na nossa lógica)
# Na prática usamos: accept < t_accept => AC; t_accept <= r < t_reneg => RENEG; r >= t_reneg => REJ

SLICE_THRESHOLDS: Dict[str, Dict[str, float]] = {
    "URLLC": {
        "accept": 0.48,
        "renegotiate": 0.72,
    },
    "eMBB": {
        "accept": 0.56,
        "renegotiate": 0.78,
    },
    "mMTC": {
        "accept": 0.54,
        "renegotiate": 0.76,
    },
}

# Fallback quando slice_type é desconhecido (mantém comportamento próximo ao legado)
DEFAULT_THRESHOLDS: Dict[str, float] = {"accept": 0.55, "renegotiate": 0.75}


def thresholds_for_slice(slice_type: str) -> Tuple[float, float, Dict[str, float]]:
    """Retorna (accept, renegotiate, dict thresholds_used)."""
    s = (slice_type or "eMBB").strip()
    u = s.upper()
    if u == "URLLC":
        key = "URLLC"
    elif u in ("EMBB", "EMB"):
        key = "eMBB"
    elif u == "MMTC":
        key = "mMTC"
    else:
        key = "eMBB"
    row = SLICE_THRESHOLDS.get(key, DEFAULT_THRESHOLDS)
    ta, tr = float(row["accept"]), float(row["renegotiate"])
    return ta, tr, {"accept": ta, "renegotiate": tr}
