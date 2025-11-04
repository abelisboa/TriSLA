from fastapi import FastAPI
from pydantic import BaseModel
import spacy, datetime, logging, requests

app = FastAPI(title="TriSLA – SEM-NSMF")
logging.basicConfig(level=logging.INFO)
nlp = spacy.load("pt_core_news_sm")

class Intent(BaseModel):
    descricao: str

@app.post("/semantic/interpret")
def interpret(i: Intent):
    doc = nlp(i.descricao)
    tipo, prioridade, qos = None, None, {}
    for token in doc:
        if token.text.upper() in ["URLLC","EMBB","MMTC"]:
            tipo = token.text.upper()
        if token.text.lower() == "prioridade":
            nxt = token.nbor(1) if token.i < len(doc)-1 else None
            if nxt: prioridade = nxt.text.lower()
        if token.text.lower().endswith("ms"):
            qos["latency"] = float(token.text.lower().replace("ms",""))
    nest = {
        "intent": "CriarSlice",
        "slice_type": tipo or "URLLC",
        "priority": prioridade or "alta",
        "qos": qos,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    requests.post("http://trisla-ai:8080/predict", json=nest)
    return nest