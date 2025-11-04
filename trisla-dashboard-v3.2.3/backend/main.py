from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx, os

app = FastAPI(title="TriSLA Dashboard API", version="3.2.3")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/status")
def status():
    return {"status": "TriSLA Dashboard API online", "version": "3.2.3"}

@app.get("/api/v1/health")
def health():
    return {"status": "ok", "phase": "operational"}

@app.get("/api/metrics")
async def metrics():
    prometheus_url = os.getenv("PROM_URL", "http://localhost:9092")
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{prometheus_url}/-/ready")
            return {"prometheus_ready": r.status_code == 200}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
