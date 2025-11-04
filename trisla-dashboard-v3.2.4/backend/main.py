from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio

app = FastAPI(title="TriSLA Dashboard API", version="3.2.4")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/status")
async def status():
    result = {
        "status": "TriSLA Dashboard API online",
        "version": "3.2.4",
        "prometheus_online": False,
        "sem_nsmf_online": False
    }

    async def check_prometheus():
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get("http://localhost:9092/-/ready")
                return r.status_code == 200
        except Exception:
            return False

    async def check_sem_nsmf():
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get("http://localhost:8090/api/v1/health")
                return r.status_code == 200
        except Exception:
            return False

    p, s = await asyncio.gather(check_prometheus(), check_sem_nsmf())
    result["prometheus_online"] = p
    result["sem_nsmf_online"] = s

    return result
