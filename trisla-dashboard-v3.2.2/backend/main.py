from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx, os

APP_VERSION = "3.2.2"
app = FastAPI(title="TriSLA Dashboard Backend", version=APP_VERSION)

# CORS for Vite dev server
origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROM_PORTS = [int(os.getenv("PROM_PORT_FALLBACK", "9090")), 9091, 9092]
SEM_PORTS  = [int(os.getenv("SEM_PORT_FALLBACK", "8080")), 8088, 8090]

async def check_url(url: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(url)
            if r.status_code == 200 and any(k in r.text.lower() for k in ("ok","running","ready","prometheus server is ready")):
                return True
    except Exception:
        pass
    return False

@app.get("/api/status")
async def status():
    prom = any([await check_url(f"http://localhost:{p}/-/ready") for p in PROM_PORTS])
    sem  = any([await check_url(f"http://localhost:{p}/api/v1/health") for p in SEM_PORTS])
    return {
        "version": APP_VERSION,
        "prometheus": "online" if prom else "offline",
        "sem_nsmf": "online" if sem else "offline",
        "ml_nsmf": "unknown",
        "bc_nssmf": "unknown"
    }
