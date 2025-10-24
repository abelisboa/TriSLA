from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests, logging, os

app = FastAPI(title="TriSLA Public API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SEMANTIC_URL = os.getenv("SEMANTIC_URL", "http://trisla-semantic:8081")
AI_URL = os.getenv("AI_URL", "http://trisla-ai:8080")
BLOCKCHAIN_URL = os.getenv("BLOCKCHAIN_URL", "http://trisla-blockchain:8051")
MONITORING_URL = os.getenv("MONITORING_URL", "http://trisla-monitoring:8090")

logging.basicConfig(level=logging.INFO)

class SLARequest(BaseModel):
    descricao: str
    slice_type: str | None = None
    qos: dict | None = None

@app.post("/api/v1/semantic")
def interpret(req: SLARequest):
    r = requests.post(f"{SEMANTIC_URL}/semantic/interpret", json={"descricao": req.descricao})
    return r.json()

@app.post("/api/v1/predict")
def predict(req: SLARequest):
    r = requests.post(f"{AI_URL}/predict", json=req.dict())
    return r.json()

@app.post("/api/v1/contracts")
def register(req: SLARequest):
    data = {
        "sla_id": f"SLA_{os.urandom(4).hex()}",
        "slice_type": req.slice_type or "URLLC",
        "decision": "ACCEPT",
        "compliance": "0.99"
    }
    r = requests.post(f"{BLOCKCHAIN_URL}/contracts/register", json=data)
    return r.json()

@app.get("/api/v1/metrics")
def metrics():
    r = requests.get(f"{MONITORING_URL}/metrics")
    return r.json()

@app.get("/api/v1/health")
def health():
    return {"status": "TriSLA Portal API running"}
