from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx, os

app = FastAPI(title="TriSLA Dashboard Backend", version="3.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROM_URL = os.getenv("PROM_URL", "http://localhost:9090/-/ready")
SEM_URL  = os.getenv("SEM_URL",  "http://localhost:8080/api/v1/health")

async def check_url(url: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=2.5) as client:
            r = await client.get(url)
            if r.status_code == 200:
                txt = r.text.lower()
                if any(k in txt for k in ["ok", "running", "ready", "prometheus server is ready"]):
                    return "online"
            return "offline"
    except Exception:
        return "offline"

@app.get("/api/status")
async def status():
    prom = await check_url(PROM_URL)
    sem  = await check_url(SEM_URL)
    return {"prometheus": prom, "sem_nsmf": sem, "ml_nsmf": "unknown", "bc_nssmf": "unknown"}
