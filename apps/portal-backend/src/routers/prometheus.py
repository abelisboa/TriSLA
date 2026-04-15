from fastapi import APIRouter, HTTPException, Query
from typing import Any, Optional

from src.services.prometheus import PrometheusService
from src.telemetry.contract_v2 import TELEMETRY_UNITS_V2
from src.telemetry.promql_ssot import PROMQL_SUMMARY
from src.utils.prometheus_response import safe_first_vector_value

router = APIRouter()
prometheus_service = PrometheusService()

_PROMQL_ALIASES = {
    # Backward-compatible aliases for RAN PRB telemetry names.
    "prb_usage": "trisla_ran_prb_utilization",
    "gnb_prb_usage": "trisla_ran_prb_utilization",
    "ran_prb_utilization": "trisla_ran_prb_utilization",
}


def _resolve_promql_alias(query: str) -> str:
    q = (query or "").strip()
    return _PROMQL_ALIASES.get(q, q)


@router.get("/")
async def prometheus_root():
    return {"status": "prometheus router active"}


@router.get("/query")
async def query_prometheus(
    query: str = Query(..., description="Prometheus query"),
    time: Optional[str] = Query(None, description="Timestamp for instant query"),
):
    """Executa query Prometheus"""
    try:
        result = await prometheus_service.query(_resolve_promql_alias(query), time)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query_range")
async def query_range_prometheus(
    query: str = Query(..., description="Prometheus query"),
    start: str = Query(..., description="Start timestamp"),
    end: str = Query(..., description="End timestamp"),
    step: str = Query(..., description="Step duration"),
):
    """Executa query range Prometheus"""
    try:
        result = await prometheus_service.query_range(
            _resolve_promql_alias(query), start, end, step
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/targets")
async def get_targets():
    """Retorna lista de targets do Prometheus"""
    try:
        targets = await prometheus_service.get_targets()
        return targets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def observability_summary():
    """
    Resumo rápido de observabilidade TriSLA:
    - disponibilidade
    - CPU
    - memória
    """
    q_throughput_mbps = PROMQL_SUMMARY["throughput_mbps"]
    q_latency_ms = PROMQL_SUMMARY["transport_latency_ms"]
    q_sessions = PROMQL_SUMMARY["sessions"]
    q_cpu_pct = PROMQL_SUMMARY["cluster_cpu_percent"]
    q_prb = PROMQL_SUMMARY["ran_prb_instant"]

    def _norm(value: Optional[float], ceiling: float) -> float:
        if value is None or ceiling <= 0:
            return 0.0
        return max(0.0, min(1.0, value / ceiling))

    try:
        throughput_resp = await prometheus_service.query(q_throughput_mbps)
        latency_resp = await prometheus_service.query(q_latency_ms)
        sessions_resp = await prometheus_service.query(q_sessions)
        cpu_resp = await prometheus_service.query(q_cpu_pct)
        prb_resp = await prometheus_service.query(q_prb)

        throughput_mbps = safe_first_vector_value(throughput_resp)
        transport_latency_ms = safe_first_vector_value(latency_resp)
        active_sessions = safe_first_vector_value(sessions_resp)
        cpu_pct = safe_first_vector_value(cpu_resp)
        ran_prb_utilization = safe_first_vector_value(prb_resp)

        # Deterministic weighted index in [0,1]
        n_thr = _norm(throughput_mbps, 50.0)
        n_lat = _norm(transport_latency_ms, 200.0)
        n_ses = _norm(active_sessions, 20.0)
        ran_load = round(0.5 * n_thr + 0.3 * n_lat + 0.2 * n_ses, 6)

        return {
            "ran_load": ran_load,
            "transport_latency": transport_latency_ms,
            "throughput_mbps": throughput_mbps,
            "sessions": active_sessions,
            "cpu": cpu_pct,
            "ran_prb_utilization": ran_prb_utilization,
            "formula": "0.5*norm(throughput,50)+0.3*norm(latency_ms,200)+0.2*norm(sessions,20)",
            "metadata": {
                "telemetry_version": "v2",
                "telemetry_units": dict(TELEMETRY_UNITS_V2),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"summary_failed: {e}")
