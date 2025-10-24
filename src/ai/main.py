from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
import random

app = FastAPI(title="TriSLA ML-NSMF", version="1.0.0")

class Metrics(BaseModel):
    features: Dict[str, float] = {}

@app.get("/health")
def health():
    return {"module": "ML-NSMF", "status": "ok"}

@app.post("/predict")
def predict(m: Metrics):
    confidence = round(random.uniform(0.80, 0.99), 3)
    return {"confidence": confidence, "features": m.features}
