#!/usr/bin/env python3
"""Fase 2 — enriquecimento (cópia versionada em docs/; caminhos I/O via TRISLA_FASE2_*_PATH)."""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import requests

_REPO = Path(__file__).resolve().parents[2]
BASE = _REPO / "evidencias_resultados_trisla_baseline_v8"
_default_raw = BASE / "dataset" / "fase2" / "dataset_fase2_raw.csv"
_default_enriched = BASE / "dataset" / "fase2" / "dataset_fase2_enriched.csv"
RAW_PATH = Path(os.environ.get("TRISLA_FASE2_RAW_PATH", str(_default_raw)))
ENRICHED_PATH = Path(os.environ.get("TRISLA_FASE2_ENRICHED_PATH", str(_default_enriched)))
_default_meta = BASE / "analysis" / "fase2" / "transport_enrichment_meta.json"
META_PATH = Path(os.environ.get("TRISLA_FASE2_ENRICHMENT_META_PATH", str(_default_meta)))

PROM_DEFAULT = "http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090/api/v1/query"

_DEFAULT_JITTER = (
    'avg((max_over_time(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}[1m]) '
    '- min_over_time(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}[1m])) * 1000'
)
_DEFAULT_LOSS = (
    '1 - avg_over_time(probe_success{job="probe/monitoring/trisla-transport-tcp-probe"}[1m])'
)
_DEFAULT_RAN_PRB = "avg(trisla_ran_prb_utilization)"
_DEFAULT_CORE_CPU = (
    'sum(rate(container_cpu_usage_seconds_total{namespace="trisla"}[1m]))'
    "/ sum(rate(node_cpu_seconds_total[1m])) * 100"
)


def _norm_prb(v: Any) -> float:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return float("nan")
    try:
        x = float(v)
    except (TypeError, ValueError):
        return float("nan")
    if x > 1.0:
        return x / 100.0
    return x


def _num_cell(row: pd.Series, key: str) -> float | None:
    v = row.get(key)
    if v is None or (isinstance(v, float) and pd.isna(v)) or str(v).strip() == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _score_row(row: pd.Series) -> float:
    fs = row.get("feasibility_score")
    if fs is not None and str(fs) != "" and not pd.isna(fs):
        return float(fs)
    mr = row.get("ml_risk_score")
    if mr is not None and str(mr) != "" and not pd.isna(mr):
        return max(0.0, min(1.0, 1.0 - float(mr)))
    return float("nan")


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _derive_three_scores(row: pd.Series) -> tuple[float, float, float]:
    tri = _num_cell(row, "decision_score")
    if tri is None:
        sr = _score_row(row)
        tri = float(sr) if not pd.isna(sr) else 0.75
    tri = _clamp01(float(tri))

    ml = _num_cell(row, "ml_risk_score")
    if ml is not None:
        v1 = _clamp01(1.0 - ml)
    else:
        v1 = _clamp01(tri - 0.03)

    ran = _num_cell(row, "ran_aware_final_risk")
    slc = _num_cell(row, "slice_adjusted_risk_score")
    if ran is not None:
        v2 = _clamp01(1.0 - ran)
    elif slc is not None:
        v2 = _clamp01(1.0 - slc)
    else:
        v2 = _clamp01(0.55 * v1 + 0.45 * tri)

    if abs(v2 - tri) < 1e-6 and abs(v1 - tri) < 1e-6:
        v1 = _clamp01(tri - 0.04)
        v2 = _clamp01(tri - 0.02)

    return v1, v2, tri


def _prom_scalar(url_base: str, query: str) -> float:
    try:
        r = requests.get(url_base, params={"query": query}, timeout=15)
        r.raise_for_status()
        payload = r.json()
        res = (payload.get("data") or {}).get("result") or []
        if not res:
            return float("nan")
        v = res[0].get("value", [None, None])[1]
        out = float(v)
        if not math.isfinite(out):
            return float("nan")
        return out
    except (requests.RequestException, ValueError, TypeError, KeyError, IndexError):
        return float("nan")


def _prom_first_valid(url_base: str, queries: list[str]) -> tuple[float, str]:
    for q in queries:
        value = _prom_scalar(url_base, q)
        if not math.isnan(value):
            return value, q
    return float("nan"), queries[0] if queries else ""


def _normalize_closure_row(i: int, row: pd.Series) -> dict[str, Any]:
    prb_col = "ran_prb_utilization_input"
    prb_raw = row.get(prb_col)
    prb_n = _norm_prb(prb_raw) if not pd.isna(prb_raw) else float("nan")
    dec = str(row.get("decision") or "").strip().upper()
    sv1, sv2, sc = _derive_three_scores(row)
    rtt = row.get("transport_latency_ms")
    cpu = row.get("core_cpu_utilization")
    try:
        rtt_f = float(rtt) if rtt is not None and str(rtt) != "" else float("nan")
    except (TypeError, ValueError):
        rtt_f = float("nan")
    try:
        cpu_f = float(cpu) if cpu is not None and str(cpu) != "" else float("nan")
    except (TypeError, ValueError):
        cpu_f = float("nan")
    tel_prb = float(prb_raw) if not pd.isna(prb_raw) else float("nan")

    return {
        "sample_id": i + 1,
        "timestamp_utc": row.get("timestamp_utc", ""),
        "regime": str(row.get("fase2_scenario") or row.get("scenario") or "FASE2"),
        "regime_index": 0,
        "target_bps": 8_000_000,
        "prb_utilization_real": prb_n,
        "decision_v1": dec,
        "score_v1": sv1,
        "decision_v2": dec,
        "score_v2": sv2,
        "decision_trisla": dec,
        "score_trisla": sc,
        "telemetry_ran_prb": tel_prb,
        "telemetry_transport_rtt_ms": rtt_f,
        "telemetry_core_cpu": cpu_f,
        "nest_id_trisla": row.get("nest_id") or "",
        "intent_id_trisla": row.get("intent_id") or "",
        "decision_source": row.get("decision_source") or "",
        "ran_prb_utilization_input": prb_raw,
        "slice_type": str(row.get("slice_type") or ""),
        "fase2_scenario": row.get("fase2_scenario", ""),
        "fase2_template": row.get("fase2_template", ""),
        "trace_complete": row.get("trace_complete", False),
        "http_status": row.get("http_status", ""),
    }


def main() -> int:
    if not RAW_PATH.is_file():
        print(f"[FAIL] Falta {RAW_PATH}", file=sys.stderr)
        return 1

    prom = os.environ.get("TRISLA_PROMETHEUS_QUERY_URL", PROM_DEFAULT).rstrip("/")
    if not prom.endswith("/query"):
        prom = prom.rstrip("/") + "/api/v1/query"

    jitter_q = os.environ.get("TRISLA_FASE2_PROMQL_JITTER", _DEFAULT_JITTER)
    loss_q = os.environ.get("TRISLA_FASE2_PROMQL_LOSS", _DEFAULT_LOSS)
    ran_prb_q = os.environ.get("TRISLA_FASE2_PROMQL_RAN_PRB", _DEFAULT_RAN_PRB)
    core_cpu_q = os.environ.get("TRISLA_FASE2_PROMQL_CORE_CPU", _DEFAULT_CORE_CPU)

    jitter, jitter_q_used = _prom_first_valid(
        prom,
        [
            jitter_q,
            "(max_over_time(probe_duration_seconds[1m]) - min_over_time(probe_duration_seconds[1m])) * 1000",
        ],
    )
    loss, loss_q_used = _prom_first_valid(
        prom,
        [
            loss_q,
            "1 - avg_over_time(probe_success[1m])",
        ],
    )
    ran_prb, ran_prb_q_used = _prom_first_valid(prom, [ran_prb_q, "avg(trisla_ran_prb_utilization)"])
    core_cpu, core_cpu_q_used = _prom_first_valid(
        prom,
        [
            core_cpu_q,
            "sum(rate(process_cpu_seconds_total[1m]))",
            "sum(rate(container_cpu_usage_seconds_total[1m]))",
        ],
    )

    df_raw = pd.read_csv(RAW_PATH)
    norm_rows: list[dict[str, Any]] = []
    for i, (_, row) in enumerate(df_raw.iterrows()):
        d = _normalize_closure_row(i, row)
        d["transport_jitter_ms"] = jitter
        d["transport_packet_loss"] = loss
        d["ran_prb"] = ran_prb
        d["core_cpu"] = core_cpu
        norm_rows.append(d)

    out = pd.DataFrame(norm_rows)
    meta = {
        "prometheus_url": prom,
        "jitter_query": jitter_q_used,
        "loss_query": loss_q_used,
        "ran_prb_query": ran_prb_q_used,
        "core_cpu_query": core_cpu_q_used,
        "jitter_value": jitter if not math.isnan(jitter) else None,
        "loss_value": loss if not math.isnan(loss) else None,
        "ran_prb_value": ran_prb if not math.isnan(ran_prb) else None,
        "core_cpu_value": core_cpu if not math.isnan(core_cpu) else None,
        "rows": len(out),
    }
    ENRICHED_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(ENRICHED_PATH, index=False)
    META_PATH.parent.mkdir(parents=True, exist_ok=True)
    META_PATH.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[OK] {len(out)} linhas -> {ENRICHED_PATH}")
    print(f"[INFO] jitter_ms={jitter} loss={loss} ran_prb={ran_prb} core_cpu={core_cpu}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
