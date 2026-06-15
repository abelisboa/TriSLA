"""
Telemetry snapshot collector (sla-agent revalidate path).

Adaptado de apps/portal-backend/src/telemetry/collector.py — apenas as funções
necessárias para `collect_domain_metrics_async`. CSV writer, settings-based config
e demais utilitários do backend NÃO foram trazidos para evitar dependências
desnecessárias no SLA-Agent.

PrometheusURL é resolvido em ordem:
1. env PROMETHEUS_URL
2. fallback `http://monitoring-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090`
   (mesmo default usado por decision-engine/src/config.py).

Não alterar semântica sem replicar a mesma mudança no backend.
"""
from __future__ import annotations

import asyncio
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx

from reliability_proxy import reliability_pct_from_packet_loss

from .contract_v2 import apply_telemetry_contract_v2
from .promql_ssot import PROMQL_SSOT
from .prometheus_response import safe_extract_result

logger = logging.getLogger(__name__)

_PROM_DEFAULT = "http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090"


def _prom_base_url() -> str:
    return os.getenv("PROMETHEUS_URL", _PROM_DEFAULT).rstrip("/")


def _promql(suffix: str) -> Optional[str]:
    v = os.getenv(f"TELEMETRY_PROMQL_{suffix}")
    if v is not None and str(v).strip():
        return str(v).strip()
    return PROMQL_SSOT.get(suffix)


def _mean_from_query_range_json(data: Any, query_hint: str = "") -> Optional[float]:
    if not isinstance(data, dict):
        return None
    if data.get("status") != "success":
        return None
    raw_result = safe_extract_result(data)
    if not raw_result:
        return None

    values: List[float] = []
    for series in raw_result:
        if not isinstance(series, dict):
            continue
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
    if not values:
        return None
    return sum(values) / len(values)


def _all_values_from_query_range_json(data: Any) -> List[float]:
    if not isinstance(data, dict) or data.get("status") != "success":
        return []
    raw_result = safe_extract_result(data)
    if not raw_result:
        return []
    out: List[float] = []
    for series in raw_result:
        if not isinstance(series, dict):
            continue
        raw_values = series.get("values")
        if not isinstance(raw_values, list) or not raw_values:
            continue
        for pair in raw_values:
            if not isinstance(pair, (list, tuple)) or len(pair) < 2:
                continue
            try:
                out.append(float(pair[1]))
            except (TypeError, ValueError):
                continue
    return out


async def _query_range_mean(
    client: httpx.AsyncClient,
    query: str,
    start: float,
    end: float,
    step: str = "1s",
) -> Optional[float]:
    url = f"{_prom_base_url()}/api/v1/query_range"
    params = {"query": query, "start": str(start), "end": str(end), "step": step}
    try:
        r = await client.get(url, params=params, timeout=httpx.Timeout(1.5))
        r.raise_for_status()
        return _mean_from_query_range_json(r.json(), query_hint=query)
    except Exception as exc:
        logger.warning("[TELEMETRY] prometheus query_range failed query=%s err=%s", query[:80], exc)
        return None


async def _query_instant_scalar(
    client: httpx.AsyncClient,
    query: str,
) -> Optional[float]:
    """Instant query for ratio/rate expressions (Sprint 7C packet_loss_pct)."""
    url = f"{_prom_base_url()}/api/v1/query"
    try:
        r = await client.get(url, params={"query": query}, timeout=httpx.Timeout(2.0))
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, dict) or data.get("status") != "success":
            return None
        results = safe_extract_result(data)
        if not results:
            return None
        val = results[0].get("value")
        if not val or len(val) < 2:
            return None
        out = float(val[1])
        if out != out:  # NaN
            return None
        return out
    except Exception as exc:
        logger.warning("[TELEMETRY] prometheus query instant failed query=%s err=%s", query[:80], exc)
        return None


async def _query_range_spread_ms(
    client: httpx.AsyncClient,
    query: str,
    start: float,
    end: float,
    step: str = "1s",
) -> Optional[float]:
    url = f"{_prom_base_url()}/api/v1/query_range"
    params = {"query": query, "start": str(start), "end": str(end), "step": step}
    try:
        r = await client.get(url, params=params, timeout=httpx.Timeout(1.5))
        r.raise_for_status()
        vals = _all_values_from_query_range_json(r.json())
        if not vals:
            return None
        return (max(vals) - min(vals)) * 1000.0
    except Exception as exc:
        logger.warning("[TELEMETRY] prometheus query_range spread failed query=%s err=%s", query[:80], exc)
        return None


async def collect_domain_metrics_async(
    execution_id: str,
    timestamp_decision_iso: Optional[str] = None,
) -> Tuple[Dict[str, Any], float]:
    """Collect domain metrics aligned to decision time window [t-2s, t]."""
    t_end = time.time()
    t_start = t_end - 2.0

    snapshot: Dict[str, Any] = {
        "execution_id": execution_id,
        "timestamp": timestamp_decision_iso or datetime.now(timezone.utc).isoformat(),
        "ran": {"prb_utilization": None, "latency": None, "reliability_pct": None},
        "transport": {
            "rtt": None,
            "jitter": None,
            "bandwidth_mbps": None,
            "packet_loss_pct": None,
        },
        "core": {"cpu": None, "memory": None, "availability_pct": None},
    }

    queries = {
        "ran_prb": (_promql("RAN_PRB"), "ran", "prb_utilization"),
        "ran_lat": (_promql("RAN_LATENCY"), "ran", "latency"),
        "trans_rtt": (_promql("TRANSPORT_RTT"), "transport", "rtt"),
        "trans_jit": (_promql("TRANSPORT_JITTER"), "transport", "jitter"),
        "core_cpu": (_promql("CORE_CPU"), "core", "cpu"),
        "core_mem": (_promql("CORE_MEMORY"), "core", "memory"),
        "trans_bw": (_promql("TRANSPORT_BANDWIDTH_MBPS"), "transport", "bandwidth_mbps"),
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

            if snapshot["transport"]["jitter"] is None:
                spread_q = 'probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}'
                sp = await _query_range_spread_ms(client, spread_q, t_start, t_end, "1s")
                if sp is not None:
                    snapshot["transport"]["jitter"] = sp

            pl_q = _promql("TRANSPORT_PACKET_LOSS_PCT")
            if pl_q:
                pl = await _query_instant_scalar(client, pl_q)
                if pl is not None:
                    snapshot["transport"]["packet_loss_pct"] = pl

            if snapshot["ran"].get("reliability_pct") is None:
                pl_obs = snapshot["transport"].get("packet_loss_pct")
                if pl_obs is not None:
                    snapshot["ran"]["reliability_pct"] = reliability_pct_from_packet_loss(
                        float(pl_obs)
                    )
                else:
                    rel_q = _promql("RELIABILITY_PROXY_PCT")
                    if rel_q:
                        rel = await _query_instant_scalar(client, rel_q)
                        if rel is not None:
                            snapshot["ran"]["reliability_pct"] = max(
                                0.0, min(100.0, float(rel))
                            )
            if snapshot["ran"].get("reliability_pct") is not None:
                snapshot["ran"]["reliability"] = snapshot["ran"]["reliability_pct"]
                snapshot["ran"][
                    "reliability_proxy_kind"
                ] = "TRANSPORT_DELIVERY_RELIABILITY_PROXY"

            av_q = _promql("CORE_AVAILABILITY_PCT")
            if av_q and snapshot["core"].get("availability_pct") is None:
                av = await _query_instant_scalar(client, av_q)
                if av is not None:
                    snapshot["core"]["availability_pct"] = av

    try:
        await asyncio.wait_for(run_queries(), timeout=3.0)
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
    apply_telemetry_contract_v2(snapshot)
    return snapshot, elapsed_ms
