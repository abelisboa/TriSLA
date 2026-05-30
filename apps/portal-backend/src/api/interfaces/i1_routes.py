from fastapi import APIRouter, HTTPException
import os
import requests

from src.telemetry.promql_ssot import CN_I1_CPU_DEFAULT, CN_I1_MEMORY_DEFAULT

router = APIRouter(prefix="/api/v1/interfaces", tags=["TriSLA I1 Runtime Interfaces"])

PROM_URL = os.getenv("PROMETHEUS_URL") or os.getenv("PROM_URL") or "http://prometheus-kube-prometheus-prometheus.monitoring.svc:9090"

def _prom_query(query: str):
    try:
        r = requests.get(f"{PROM_URL}/api/v1/query", params={"query": query}, timeout=5)
        r.raise_for_status()
        data = r.json()
        result = data.get("data", {}).get("result", [])
        if not result:
            return None
        return float(result[0]["value"][1])
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Prometheus query failed: {exc}")

@router.get("/ran-i1/metrics")
def ran_i1_metrics():
    value = _prom_query(
        os.getenv(
            "RAN_I1_PRB_QUERY",
            'avg(trisla_ran_prb_utilization{job="trisla-ran-ue-upf-proxy"})',
        )
    )
    return {
        "interface": "RAN-I1",
        "version": "v1",
        "source": "prometheus",
        "metrics": {
            "prb_utilization": value
        }
    }

@router.get("/tn-i1/metrics")
def tn_i1_metrics():
    jitter = _prom_query(os.getenv("TN_I1_JITTER_QUERY", "avg(trisla_transport_jitter_ms)"))
    latency = _prom_query(os.getenv("TN_I1_LATENCY_QUERY", "avg(trisla_transport_latency_ms)"))
    return {
        "interface": "TN-I1",
        "version": "v1",
        "source": "prometheus",
        "metrics": {
            "latency_ms": latency,
            "jitter_ms": jitter
        }
    }

@router.get("/cn-i1/metrics")
def cn_i1_metrics():
    cpu = _prom_query(os.getenv("CN_I1_CPU_QUERY", CN_I1_CPU_DEFAULT))
    memory = _prom_query(os.getenv("CN_I1_MEMORY_QUERY", CN_I1_MEMORY_DEFAULT))
    return {
        "interface": "CN-I1",
        "version": "v1",
        "source": "prometheus",
        "metrics": {
            "cpu_utilization": cpu,
            "memory_utilization": memory
        }
    }
