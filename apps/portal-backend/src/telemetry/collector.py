"""
Telemetry snapshot: real Prometheus query_range over [t-2s, t], mean per series.
No synthetic defaults — missing queries or failures yield null.
"""
from __future__ import annotations

import asyncio
import csv
import logging
import os
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union

import httpx

from src.config import settings
from src.telemetry.contract_v2 import apply_telemetry_contract_v2
from src.telemetry.promql_ssot import PROMQL_SSOT
from src.utils.prometheus_response import safe_extract_result

logger = logging.getLogger(__name__)

_csv_lock = threading.Lock()

# PromQL: env TELEMETRY_PROMQL_* overrides; else SSOT (promql_ssot.PROMQL_SSOT).


def _prom_base_url() -> str:
    return os.getenv("PROMETHEUS_URL", settings.prometheus_url).rstrip("/")


def _promql(suffix: str) -> Optional[str]:
    v = os.getenv(f"TELEMETRY_PROMQL_{suffix}")
    if v is not None and str(v).strip():
        return str(v).strip()
    return PROMQL_SSOT.get(suffix)


def _mean_from_query_range_json(data: Any, query_hint: str = "") -> Optional[float]:
    """Average all sample values in a Prometheus query_range JSON response."""
    if not isinstance(data, dict):
        logger.debug(
            "[TELEMETRY DEBUG] result_type=%s values_count=0 query=%s",
            type(data).__name__,
            query_hint[:120] if query_hint else "",
        )
        return None
    if data.get("status") != "success":
        return None
    raw_result = safe_extract_result(data)
    if not raw_result:
        logger.debug(
            "[TELEMETRY DEBUG] result_type=no_valid_series values_count=0 query=%s",
            query_hint[:120] if query_hint else "",
        )
        return None

    values: List[float] = []
    metric_names: List[str] = []
    for series in raw_result:
        if not isinstance(series, dict):
            continue
        m = series.get("metric")
        if isinstance(m, dict):
            name = m.get("__name__") or ""
            if name:
                metric_names.append(str(name))
        raw_values = series.get("values")
        if not isinstance(raw_values, list) or not raw_values:
            continue
        for pair in raw_values:
            if not isinstance(pair, (list, tuple)) or len(pair) < 2:
                continue
            try:
                values.append(float(pair[1]))
            except (TypeError, ValueError):
                continue

    mn = metric_names[0] if metric_names else ""
    logger.debug(
        "[TELEMETRY DEBUG] result_type=matrix values_count=%s metric_name=%s query=%s",
        len(values),
        mn,
        query_hint[:120] if query_hint else "",
    )
    if not values:
        return None
    return sum(values) / len(values)


async def _query_range_mean(
    client: httpx.AsyncClient,
    query: str,
    start: float,
    end: float,
    step: str = "1s",
) -> Optional[float]:
    url = f"{_prom_base_url()}/api/v1/query_range"
    params = {
        "query": query,
        "start": str(start),
        "end": str(end),
        "step": step,
    }
    try:
        r = await client.get(url, params=params, timeout=httpx.Timeout(1.5))
        r.raise_for_status()
        return _mean_from_query_range_json(r.json(), query_hint=query)
    except Exception as exc:
        logger.warning("[TELEMETRY] prometheus query_range failed query=%s err=%s", query[:80], exc)
        return None


async def collect_domain_metrics_async(
    execution_id: str,
    timestamp_decision_iso: Optional[str] = None,
) -> Tuple[Dict[str, Any], float]:
    """
    Collect domain metrics aligned to decision time window [t-2s, t].
    Returns (telemetry_snapshot_dict, elapsed_ms).
    """
    t_end = time.time()
    t_start = t_end - 2.0

    snapshot: Dict[str, Any] = {
        "execution_id": execution_id,
        "timestamp": timestamp_decision_iso
        or datetime.now(timezone.utc).isoformat(),
        "ran": {"prb_utilization": None, "latency": None},
        "transport": {"rtt": None, "jitter": None},
        "core": {"cpu": None, "memory": None},
    }

    queries = {
        "ran_prb": (_promql("RAN_PRB"), "ran", "prb_utilization"),
        "ran_lat": (_promql("RAN_LATENCY"), "ran", "latency"),
        "trans_rtt": (_promql("TRANSPORT_RTT"), "transport", "rtt"),
        "trans_jit": (_promql("TRANSPORT_JITTER"), "transport", "jitter"),
        "core_cpu": (_promql("CORE_CPU"), "core", "cpu"),
        "core_mem": (_promql("CORE_MEMORY"), "core", "memory"),
    }

    t0 = time.perf_counter()

    async def run_queries():
        async with httpx.AsyncClient() as client:
            keys_order: List[str] = []
            tasks = []
            for key, (q, domain, field) in queries.items():
                if not q:
                    continue
                keys_order.append(key)
                tasks.append(_query_range_mean(client, q, t_start, t_end, "1s"))

            if not tasks:
                return

            results = await asyncio.gather(*tasks, return_exceptions=True)
            if not isinstance(results, list):
                logger.warning(
                    "[TELEMETRY] gather returned non-list type=%s execution_id=%s",
                    type(results).__name__,
                    execution_id,
                )
                return
            for key, res in zip(keys_order, results):
                if isinstance(res, Exception):
                    continue
                _, domain, field = queries[key]
                if res is not None:
                    snapshot[domain][field] = res

    try:
        await asyncio.wait_for(run_queries(), timeout=2.0)
    except asyncio.TimeoutError:
        logger.warning(
            "[TELEMETRY] execution_id=%s metrics_collected=false latency_ms=%.2f (timeout)",
            execution_id,
            (time.perf_counter() - t0) * 1000,
        )
        apply_telemetry_contract_v2(snapshot)
        return snapshot, (time.perf_counter() - t0) * 1000
    except Exception as exc:
        logger.warning("[TELEMETRY] execution_id=%s collect error: %s", execution_id, exc)

    elapsed_ms = (time.perf_counter() - t0) * 1000
    collected = (
        snapshot["ran"]["prb_utilization"] is not None
        or snapshot["ran"]["latency"] is not None
        or snapshot["transport"]["rtt"] is not None
        or snapshot["transport"]["jitter"] is not None
        or snapshot["core"]["cpu"] is not None
        or snapshot["core"]["memory"] is not None
    )
    logger.info(
        "[TELEMETRY] execution_id=%s metrics_collected=%s latency_ms=%.2f",
        execution_id,
        collected,
        elapsed_ms,
    )
    apply_telemetry_contract_v2(snapshot)
    return snapshot, elapsed_ms


def append_telemetry_csv(
    csv_path: Optional[str],
    row: Dict[str, Any],
) -> None:
    """Append one row if path is set and writable. Never raises to caller."""
    if not csv_path or not str(csv_path).strip():
        return
    path = str(csv_path).strip()
    fieldnames = [
        "execution_id",
        "timestamp_decision",
        "decision",
        "ml_risk_score",
        "nasp_latency_ms",
        "nasp_latency_available",
        "ran_prb",
        "ran_latency",
        "transport_rtt",
        "transport_jitter",
        "core_cpu",
        "core_memory",
        "scenario",
        "slice_type",
    ]
    try:
        with _csv_lock:
            file_exists = os.path.isfile(path)
            with open(path, "a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                if not file_exists:
                    w.writeheader()
                w.writerow(row)
    except Exception as exc:
        logger.warning("[TELEMETRY] csv append failed path=%s err=%s", path, exc)


def _csv_val(v: Union[float, int, str, None]) -> Union[float, int, str]:
    return "" if v is None else v


def build_csv_row(
    execution_id: str,
    ts: str,
    decision: str,
    ml_risk: Optional[float],
    telemetry: Dict[str, Any],
    scenario: str,
    slice_type: str,
    nasp_latency_ms: Optional[float] = None,
    nasp_latency_available: Optional[bool] = None,
) -> Dict[str, Any]:
    return {
        "execution_id": execution_id,
        "timestamp_decision": ts,
        "decision": decision,
        "ml_risk_score": _csv_val(ml_risk),
        "nasp_latency_ms": _csv_val(nasp_latency_ms),
        "nasp_latency_available": (
            "" if nasp_latency_available is None else (1 if nasp_latency_available else 0)
        ),
        "ran_prb": _csv_val(telemetry.get("ran", {}).get("prb_utilization")),
        "ran_latency": _csv_val(telemetry.get("ran", {}).get("latency")),
        "transport_rtt": _csv_val(telemetry.get("transport", {}).get("rtt")),
        "transport_jitter": _csv_val(telemetry.get("transport", {}).get("jitter")),
        "core_cpu": _csv_val(telemetry.get("core", {}).get("cpu")),
        "core_memory": _csv_val(telemetry.get("core", {}).get("memory")),
        "scenario": scenario,
        "slice_type": slice_type,
    }
