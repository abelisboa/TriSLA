
import os, asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090")

SEM_NSMF_URL = os.getenv("SEM_NSMF_URL")
SEM_NSMF_TOKEN = os.getenv("SEM_NSMF_TOKEN", "")
SEM_NSMF_NLP_PATH = os.getenv("SEM_NSMF_NLP_PATH", "/api/npl/create")
SEM_NSMF_GST_PATH = os.getenv("SEM_NSMF_GST_PATH", "/api/gst/submit")

app = FastAPI(title="TriSLA Dashboard API", version="2.1.0",
              description="Proxy API para Prometheus + integração SEM-NSMF (NASP) com fallback mock.")

origins = ["http://localhost:5173","http://127.0.0.1:5173","http://localhost:3000","http://127.0.0.1:3000"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

class PromQuery(BaseModel):
    query: str
class NPLRequest(BaseModel):
    prompt: str
class GSTTemplate(BaseModel):
    serviceName: str
    serviceDescription: Optional[str] = None
    serviceType: Optional[str] = None
    latency: Optional[str] = None
    throughput: Optional[str] = None
    availability: Optional[str] = None
    reliability: Optional[str] = None
    mobility: Optional[str] = None
    areaCoverage: Optional[str] = None
    domains: Optional[List[str]] = None
    governance: Optional[Dict[str, Any]] = None

SLICES: List[Dict[str, Any]] = []

@app.get("/")
async def root():
    return {"service": "trisla-dashboard-backend", "version": "2.1.0"}

@app.get("/health")
async def health_backend():
    return {"status":"ok","service":"trisla-dashboard-backend","timestamp":datetime.utcnow().isoformat()+"Z","prometheus":"unknown","sem_nsmf_connected":bool(SEM_NSMF_URL)}

@app.get("/api/config")
async def config_api():
    return {"prometheus_url":PROMETHEUS_URL,"sem_nsmf_url":SEM_NSMF_URL,"sem_nsmf_nlp_path":SEM_NSMF_NLP_PATH,"sem_nsmf_gst_path":SEM_NSMF_GST_PATH}

@app.get("/api/prometheus/health")
async def health_prometheus():
    url = f"{PROMETHEUS_URL}/-/ready"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(url)
            ok = r.status_code == 200
            return {"status":"ok" if ok else "error","prometheus":"ready" if ok else "not-ready","code":r.status_code,"url":url}
    except Exception as e:
        return {"status":"error","prometheus":"unreachable","error":str(e),"url":url}

async def _prom_query(query: str) -> Dict[str, Any]:
    url = f"{PROMETHEUS_URL}/api/v1/query"
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url, params={"query":query})
        r.raise_for_status()
        return r.json()

@app.post("/api/prometheus/query")
async def prom_query(body: PromQuery):
    try:
        return await _prom_query(body.query)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Prometheus error: {e}")

@app.get("/api/prometheus/metrics/system")
async def metrics_system():
    cpu_q = '100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)'
    mem_q = '(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / 1024 / 1024'
    results = {"cpu": None, "memory_mb": None}
    try:
        data_cpu, data_mem = await asyncio.gather(_prom_query(cpu_q), _prom_query(mem_q))
        def val(d):
            try:
                return float(d["data"]["result"][0]["value"][1])
            except Exception:
                return None
        results["cpu"] = val(data_cpu)
        results["memory_mb"] = val(data_mem)
    except Exception:
        pass
    return {"status":"ok","cpu_avg":results["cpu"],"memory_mb":results["memory_mb"],"timestamp":datetime.utcnow().isoformat()+"Z"}

@app.get("/api/prometheus/metrics/timeseries")
async def metrics_timeseries(metric: str = Query(default="node_cpu_seconds_total")):
    end = int(datetime.utcnow().timestamp())
    start = end - 300
    step = 5
    url = f"{PROMETHEUS_URL}/api/v1/query_range"
    params = {"query": f"rate({metric}[1m])", "start": start, "end": end, "step": step}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        return {"status":"error","error":str(e),"url":url,"params":params}

def _sem_headers() -> Dict[str, str]:
    h = {"Content-Type":"application/json"}
    if SEM_NSMF_TOKEN:
        h["Authorization"] = f"Bearer {SEM_NSMF_TOKEN}"
    return h

async def _forward_sem_post(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if not SEM_NSMF_URL:
        raise RuntimeError("SEM_NSMF_URL not configured")
    url = SEM_NSMF_URL.rstrip("/") + path
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(url, json=payload, headers=_sem_headers())
        r.raise_for_status()
        return r.json()

@app.post("/api/slices/nlp/create")
async def slices_nlp_create(req: NPLRequest):
    if SEM_NSMF_URL:
        try:
            data = await _forward_sem_post(SEM_NSMF_NLP_PATH, {"prompt": req.prompt})
            SLICES.append({"id": len(SLICES)+1, "source":"NPL", "nest": data.get("generated_nest") or data, "status": data.get("status","created"), "created_at": datetime.utcnow().isoformat()+"Z"})
            return data
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"SEM-NSMF error: {e}")
    text = req.prompt.lower()
    if any(k in text for k in ["cirurgia","latência","baixa latência","controle remoto"]):
        nstype = "URLLC"
    elif any(k in text for k in ["vídeo","streaming","banda","hd"]):
        nstype = "eMBB"
    elif any(k in text for k in ["iot","sensor","telemetria","muitos dispositivos"]):
        nstype = "mMTC"
    else:
        nstype = "eMBB"
    nest = {"name": f"slice_{nstype.lower()}_{len(SLICES)+1:03d}","type": nstype,"domains": ["RAN","Transport","Core"],"sla": {"latency":"<=1ms" if nstype=="URLLC" else "<=30ms","availability":"99.99%"}}
    SLICES.append({"id": len(SLICES)+1, "source":"NPL", "nest":nest, "status":"created", "created_at": datetime.utcnow().isoformat()+"Z"})
    return {"status":"ok","detected_type":nstype,"generated_nest":nest,"slice_id":len(SLICES)}

@app.post("/api/slices/gst/submit")
async def slices_gst_submit(tpl: GSTTemplate):
    if SEM_NSMF_URL:
        try:
            data = await _forward_sem_post(SEM_NSMF_GST_PATH, tpl.dict())
            SLICES.append({"id": len(SLICES)+1, "source":"GST", "tpl": tpl.dict(), "nest": data.get("generated_nest") or data, "status": data.get("status","validated"), "created_at": datetime.utcnow().isoformat()+"Z"})
            return data
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"SEM-NSMF error: {e}")
    nstype = tpl.serviceType or "eMBB"
    nest = {"name": f"{tpl.serviceName.replace(' ','_').lower()}_{len(SLICES)+1:03d}",
            "type": nstype, "domains": tpl.domains or ["RAN","Transport","Core"],
            "sla": {"latency": tpl.latency or ("<=1ms" if nstype=="URLLC" else "<=30ms"),
                    "throughput": tpl.throughput or "100Mbps",
                    "availability": tpl.availability or "99.9%"},
            "governance": tpl.governance or {"tenant":"default"}}
    SLICES.append({"id": len(SLICES)+1, "source":"GST", "tpl":tpl.dict(), "nest":nest, "status":"validated", "created_at": datetime.utcnow().isoformat()+"Z"})
    return {"status":"validated","generated_nest":nest,"slice_id":len(SLICES)}

@app.get("/api/slices/list")
async def slices_list():
    return {"count": len(SLICES), "items": SLICES}
