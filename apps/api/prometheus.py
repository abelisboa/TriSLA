"""
TriSLA Prometheus API - Conexão direta sem Grafana
"""
from fastapi import APIRouter, HTTPException
import httpx
import os
from typing import Dict, List
from datetime import datetime

router = APIRouter(prefix="/prometheus", tags=["Prometheus"])

PROMETHEUS_URL = os.getenv(
    "PROM_URL", 
    "http://hibrido-prometheus.monitoring.svc.cluster.local:9090"
).replace("/api/v1/query", "")

async def query_prometheus(query: str) -> List[Dict]:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{PROMETHEUS_URL}/api/v1/query",
                params={"query": query}
            )
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "success":
                return data.get("data", {}).get("result", [])
            return []
    except Exception as e:
        print(f"Erro: {e}")
        return []

async def query_range_prometheus(query: str, start: int, end: int, step: str = "15s") -> List[Dict]:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{PROMETHEUS_URL}/api/v1/query_range",
                params={"query": query, "start": start, "end": end, "step": step}
            )
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "success":
                return data.get("data", {}).get("result", [])
            return []
    except Exception as e:
        print(f"Erro: {e}")
        return []

@router.get("/health")
async def prometheus_health():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{PROMETHEUS_URL}/api/v1/status/config")
            response.raise_for_status()
            return {"status": "ok", "prometheus": "accessible"}
    except Exception as e:
        return {"status": "error", "prometheus": "unreachable", "error": str(e)}

@router.get("/metrics/slices")
async def get_slices_metrics():
    queries = {
        "total": "count(trisla_slices_active)",
        "by_type": "sum by (slice_type) (trisla_slices_active)",
        "created_total": "trisla_slices_created_total",
    }
    results = {}
    for key, query in queries.items():
        results[key] = await query_prometheus(query)
    return results

@router.get("/metrics/system")
async def get_system_metrics():
    queries = {
        "components_up": "up{job=~'trisla.*'}",
        "cpu_usage": "rate(container_cpu_usage_seconds_total{pod=~'trisla.*'}[5m]) * 100",
        "memory_usage": "container_memory_usage_bytes{pod=~'trisla.*'} / 1024 / 1024",
        "http_requests": "rate(http_requests_total{job=~'trisla.*'}[5m])",
    }
    results = {}
    for key, query in queries.items():
        results[key] = await query_prometheus(query)
    return results

@router.get("/metrics/jobs")
async def get_jobs_metrics():
    queries = {
        "completed": "trisla_jobs_completed_total",
        "failed": "trisla_jobs_failed_total",
        "active": "trisla_jobs_active_total",
    }
    results = {}
    for key, query in queries.items():
        results[key] = await query_prometheus(query)
    return results

@router.get("/metrics/timeseries")
async def get_timeseries_metrics(metric: str = "http_requests_total", range_minutes: int = 60, step: str = "15s"):
    end = int(datetime.now().timestamp())
    start = end - (range_minutes * 60)
    query = f"rate({metric}{{job=~'trisla.*'}}[5m])"
    results = await query_range_prometheus(query, start, end, step)
    timeseries_data = []
    for result in results:
        metric_name = result.get("metric", {}).get("job", metric)
        for value_pair in result.get("values", []):
            timeseries_data.append({
                "time": datetime.fromtimestamp(value_pair[0]).isoformat(),
                "timestamp": value_pair[0],
                "value": float(value_pair[1]),
                "metric": metric_name
            })
    return {"data": timeseries_data, "metric": metric}

@router.post("/query")
async def execute_custom_query(query: str):
    if not query:
        raise HTTPException(status_code=400, detail="Query não pode ser vazia")
    results = await query_prometheus(query)
    return {"status": "success", "data": results}
