from fastapi import FastAPI
from pydantic import BaseModel
import joblib, shap, numpy as np, datetime, logging, requests

app = FastAPI(title="TriSLA – ML-NSMF")
logging.basicConfig(level=logging.INFO)
model = joblib.load("modelo_sla.pkl")
explainer = shap.Explainer(model)

class Nest(BaseModel):
    slice_type: str
    priority: str
    qos: dict

@app.post("/predict")
def predict(n: Nest):
    features = np.array([[float(n.qos.get("latency",5)), 1 if n.slice_type=="URLLC" else 0]])
    y_pred = model.predict(features)[0]
    shap_vals = explainer(features)
    explain = dict(zip(["latency","urlcc_flag"], shap_vals[0].values.tolist()))
    decision = "ACCEPT" if y_pred>0.5 else "REJECT"
    payload = {
        "sla_id": f"SLA-{datetime.datetime.utcnow().timestamp()}",
        "slice_type": n.slice_type,
        "decision": decision,
        "compliance": str(round(float(y_pred),2))
    }
    requests.post("http://trisla-blockchain:8051/contracts/register", json=payload)
    return {"decision": decision, "explanation": explain}