
import asyncio
import random
from datetime import datetime
from typing import Optional, Dict, Any

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Import configuration
from config import config

app = FastAPI(title="TriSLA Dashboard Backend", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get configuration values
PROMETHEUS_URL = config.prometheus.url.rstrip("/")
SEM_NSMF_URL = config.sem_nsmf.url.rstrip("/") if config.sem_nsmf.url else ""
SEM_NSMF_TOKEN = config.sem_nsmf.token or ""
SEM_NSMF_NLP_PATH = "/api/npl/create"
SEM_NSMF_GST_PATH = "/api/gst/submit"

SLICES: list[Dict[str, Any]] = []

def _first_value_float(resp: dict) -> Optional[float]:
    try:
        return float(resp["data"]["result"][0]["value"][1])
    except Exception:
        return None

def _avg_vector(resp: dict) -> Optional[float]:
    try:
        vals = [float(r["value"][1]) for r in resp["data"]["result"]]
        return sum(vals) / len(vals) if vals else None
    except Exception:
        return None

async def _prom_query(q: str) -> dict:
    url = f"{PROMETHEUS_URL}/api/v1/query"
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url, params={"query": q})
        r.raise_for_status()
        return r.json()

async def _forward_sem_post(path: str, payload: dict) -> dict:
    if not SEM_NSMF_URL:
        raise HTTPException(status_code=400, detail="SEM_NSMF_URL não configurado.")
    url = f"{SEM_NSMF_URL}{path}"
    headers = {}
    if SEM_NSMF_TOKEN:
        headers["Authorization"] = f"Bearer {SEM_NSMF_TOKEN}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(url, json=payload, headers=headers)
        r.raise_for_status()
        return r.json()

@app.get("/")
def root():
    return {
        "service": "trisla-dashboard-backend", 
        "version": "3.0.0",
        "prometheus_url": PROMETHEUS_URL,
        "sem_nsmf_url": SEM_NSMF_URL
    }

@app.get("/api/config")
async def get_config():
    """Get public configuration"""
    return {
        "prometheus_url": PROMETHEUS_URL,
        "sem_nsmf_url": SEM_NSMF_URL,
        "has_sem_nsmf_token": bool(SEM_NSMF_TOKEN)
    }

@app.get("/health")
async def health():
    return {"status": "ok", "prometheus_url": PROMETHEUS_URL}

@app.get("/api/prometheus/health")
async def prom_health():
    try:
        url = f"{PROMETHEUS_URL}/-/ready"
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(url)
            ready = r.status_code == 200 and "Ready" in r.text
            return {"status": "ok" if ready else "error", "code": r.status_code}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/prometheus/metrics/system")
async def metrics_system():
    cpu_q = '100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)'
    mem_q = '(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / 1024 / 1024'
    results = {"cpu": None, "memory_mb": None}
    try:
        data_cpu, data_mem = await asyncio.gather(_prom_query(cpu_q), _prom_query(mem_q))
        results["cpu"] = _avg_vector(data_cpu) or _first_value_float(data_cpu)
        results["memory_mb"] = _avg_vector(data_mem) or _first_value_float(data_mem)
    except Exception:
        pass
    return {
        "status": "ok",
        "cpu_avg": results["cpu"],
        "memory_mb": results["memory_mb"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

@app.get("/api/prometheus/metrics/timeseries")
async def metrics_timeseries(metric: str = Query(default="cpu_total")):
    end = int(datetime.utcnow().timestamp())
    start = end - 300
    step = 5
    if metric == "cpu_total":
        prom_query = '100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)'
    else:
        prom_query = f"rate({metric}[1m])"
    url = f"{PROMETHEUS_URL}/api/v1/query_range"
    params = {"query": prom_query, "start": start, "end": end, "step": step}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        return {"status": "error", "error": str(e), "url": url, "params": params}

@app.get("/api/prometheus/metrics/components")
async def metrics_components():
    total_q = "sum(up == 1)"
    by_job_q = "sum by(job) (up == 1)"
    try:
        total_resp, by_job_resp = await asyncio.gather(
            _prom_query(total_q), _prom_query(by_job_q)
        )
        total = _first_value_float(total_resp)
        by_job = {}
        try:
            for r in by_job_resp["data"]["result"]:
                job = r["metric"].get("job", "unknown")
                by_job[job] = float(r["value"][1])
        except Exception:
            pass
        return {"status": "ok", "total_up": total, "by_job": by_job}
    except Exception as e:
        return {"status": "error", "error": str(e)}

from pydantic import BaseModel, Field

class NPLRequest(BaseModel):
    prompt: str = Field(..., min_length=4)

class GSTTemplate(BaseModel):
    name: str
    type: str
    latency: str
    throughput: str
    availability: str
    domains: str

SLICES: list[Dict[str, Any]] = []

@app.get("/api/slices/list")
async def slices_list():
    return {"count": len(SLICES), "items": SLICES}

@app.post("/api/slices/nlp/create")
async def slices_nlp_create(req: NPLRequest):
    if SEM_NSMF_URL:
        try:
            data = await _forward_sem_post(SEM_NSMF_NLP_PATH, {"prompt": req.prompt})
            SLICES.append({
                "id": len(SLICES)+1,
                "source":"NPL",
                "name": data.get("service_name") or f"npl-{len(SLICES)+1}",
                "nest": data.get("generated_nest") or data,
                "status": data.get("status","created"),
                "created_at": datetime.utcnow().isoformat()+"Z"
            })
            return data
        except httpx.ConnectError as e:
            raise HTTPException(status_code=502, detail=f"SEM-NSMF indisponível (conexão). Dica: faça port-forward do serviço SEM-NSMF e exporte SEM_NSMF_URL. Detalhe: {e}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"SEM-NSMF erro de requisição. Detalhe: {e}")
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"SEM-NSMF error: {e}")
    nest = {"slice": {"name": f"npl-{len(SLICES)+1}", "type": "URLLC"}}
    SLICES.append({
        "id": len(SLICES)+1,
        "source":"NPL",
        "name": nest["slice"]["name"],
        "nest": nest,
        "status":"created",
        "created_at": datetime.utcnow().isoformat()+"Z"
    })
    return {"generated_nest": nest, "status":"created"}

@app.post("/api/slices/gst/submit")
async def slices_gst_submit(tpl: GSTTemplate):
    if SEM_NSMF_URL:
        try:
            data = await _forward_sem_post(SEM_NSMF_GST_PATH, tpl.dict())
            SLICES.append({
                "id": len(SLICES)+1,
                "source":"GST",
                "name": tpl.name,
                "tpl": tpl.dict(),
                "nest": data.get("generated_nest") or data,
                "status": data.get("status","validated"),
                "created_at": datetime.utcnow().isoformat()+"Z"
            })
            return data
        except httpx.ConnectError as e:
            raise HTTPException(status_code=502, detail=f"SEM-NSMF indisponível (DNS/porta). Rode: kubectl port-forward svc/<sem-nsmf> 8000:8000 e exporte SEM_NSMF_URL=http://localhost:8000. Detalhe: {e}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"SEM-NSMF erro de requisição. Detalhe: {e}")
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"SEM-NSMF error: {e}")
    nest = {"slice": {"name": tpl.name, "type": tpl.type}}
    SLICES.append({
        "id": len(SLICES)+1,
        "source":"GST",
        "name": tpl.name,
        "tpl": tpl.dict(),
        "nest": nest,
        "status":"validated",
        "created_at": datetime.utcnow().isoformat()+"Z"
    })
    return {"generated_nest": nest, "status":"validated"}

@app.get("/api/metrics/by-slice")
async def metrics_by_slice(name: str):
    try:
        cpu_q = f'100 - (avg(rate(node_cpu_seconds_total{{mode="idle", slice="{name}"}}[1m])) * 100)'
        mem_q = f'(node_memory_MemTotal_bytes{{slice="{name}"}} - node_memory_MemAvailable_bytes{{slice="{name}"}}) / 1024 / 1024'
        data_cpu, data_mem = await asyncio.gather(_prom_query(cpu_q), _prom_query(mem_q))
        cpu_val = _avg_vector(data_cpu)
        mem_val = _avg_vector(data_mem)
        if cpu_val is None and mem_val is None:
            cpu_val = 8.2 + random.random() * 3
            mem_val = 3000 + random.random() * 2000
            mode = "mock"
        else:
            mode = "real"
        return {"status": "ok", "slice": name, "cpu": cpu_val, "memory_mb": mem_val, "mode": mode}
    except Exception as e:
        return {"status": "error", "error": str(e), "slice": name}

@app.get("/api/admin/checks")
async def admin_checks():
    results = {"prometheus": "offline", "sem_nsmf": "offline"}
    try:
        r = await _prom_query("up")
        if r.get("status") == "success":
            results["prometheus"] = "online"
    except Exception:
        pass
    if SEM_NSMF_URL:
        try:
            async with httpx.AsyncClient(timeout=5.0) as c:
                r = await c.get(f"{SEM_NSMF_URL}/health")
                results["sem_nsmf"] = "online" if r.status_code < 400 else "error"
        except Exception:
            pass
    return results
