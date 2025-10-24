from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="TriSLA Integration Gateway", version="1.0.0")

class SLARequest(BaseModel):
    service: str
    slice_type: str

@app.get("/health")
def health():
    return {"module": "Integration", "status": "ok"}

@app.post("/validate_sla")
def validate_sla(req: SLARequest):
    return {"service": req.service, "slice_type": req.slice_type, "validated": True}
