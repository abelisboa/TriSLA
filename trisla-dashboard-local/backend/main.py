"""
TriSLA Dashboard Backend - Proxy para Prometheus
Conecta ao Prometheus via túnel SSH (localhost:9090)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

app = FastAPI(
    title="TriSLA Dashboard API",
    description="Proxy API para Prometheus e TriSLA",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URL do Prometheus (via túnel SSH - localhost:9090)
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090")

# Cliente HTTP async
client = httpx.AsyncClient(timeout=30.0)


async def query_prometheus(query: str) -> List[Dict]:
    """Executa query PromQL no Prometheus"""
    try:
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
        print(f"Erro ao query Prometheus: {e}")
        return []


async def query_range_prometheus(query: str, start: int, end: int, step: str = "15s") -> List[Dict]:
    """Executa query range no Prometheus"""
    try:
        response = await client.get(
            f"{PROMETHEUS_URL}/api/v1/query_range",
            params={
                "query": query,
                "start": start,
                "end": end,
                "step": step
            }
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "success":
            return data.get("data", {}).get("result", [])
        return []
    except Exception as e:
        print(f"Erro ao query range Prometheus: {e}")
        return []


@app.get("/")
async def root():
    return {
        "message": "TriSLA Dashboard API",
        "version": "1.0.0",
        "prometheus_url": PROMETHEUS_URL
    }


@app.get("/health")
async def health():
    """Health check"""
    try:
        response = await client.get(f"{PROMETHEUS_URL}/api/v1/status/config", timeout=5.0)
        response.raise_for_status()
        return {
            "status": "ok",
            "prometheus": "accessible",
            "url": PROMETHEUS_URL
        }
    except Exception as e:
        return {
            "status": "error",
            "prometheus": "unreachable",
            "error": str(e),
            "url": PROMETHEUS_URL
        }


@app.get("/api/prometheus/health")
async def prometheus_health():
    """Verifica se Prometheus está acessível"""
    return await health()


@app.get("/api/prometheus/metrics/slices")
async def get_slices_metrics():
    """Métricas de slices ativos"""
    queries = {
        "total": "count(trisla_slices_active)",
        "by_type": "sum by (slice_type) (trisla_slices_active)",
        "created_total": "trisla_slices_created_total",
    }
    
    results = {}
    for key, query in queries.items():
        results[key] = await query_prometheus(query)
    
    return results


@app.get("/api/prometheus/metrics/system")
async def get_system_metrics():
    """Métricas do sistema TriSLA"""
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


@app.get("/api/prometheus/metrics/jobs")
async def get_jobs_metrics():
    """Métricas de jobs"""
    queries = {
        "completed": "trisla_jobs_completed_total",
        "failed": "trisla_jobs_failed_total",
        "active": "trisla_jobs_active_total",
    }
    
    results = {}
    for key, query in queries.items():
        results[key] = await query_prometheus(query)
    
    return results


@app.get("/api/prometheus/metrics/timeseries")
async def get_timeseries_metrics(
    metric: str = "http_requests_total",
    range_minutes: int = 60,
    step: str = "15s"
):
    """Retorna série temporal de uma métrica para gráficos"""
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


@app.post("/api/prometheus/query")
async def execute_custom_query(query: str):
    """Executa query PromQL customizada"""
    if not query:
        raise HTTPException(status_code=400, detail="Query não pode ser vazia")
    
    results = await query_prometheus(query)
    return {"status": "success", "data": results}


@app.on_event("shutdown")
async def shutdown():
    """Cleanup"""
    await client.aclose()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)