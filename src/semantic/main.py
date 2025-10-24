from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="TriSLA SEM-NSMF", version="1.0.0")

class OntologyIn(BaseModel):
    ontology: Optional[str] = None
    query: Optional[str] = None

@app.get("/health")
def health():
    return {"module": "SEM-NSMF", "status": "ok"}

@app.post("/parse_ontology")
def parse_ontology(body: OntologyIn):
    return {"parsed": True, "len_ontology": len(body.ontology or ""), "query": body.query}
