from fastapi import FastAPI
import requests, datetime

app = FastAPI(title="TriSLA – NWDAF-like")
PROM_URL="http://prometheus.monitoring:9090"

@app.get("/metrics")
def metrics():
    q = {'query':'avg(latency_ms[1m])'}
    r = requests.get(f"{PROM_URL}/api/v1/query", params=q)
    data = r.json().get("data",{}).get("result",[])
    val = float(data[0]["value"][1]) if data else None
    return {"timestamp": datetime.datetime.utcnow().isoformat(),"latency_avg_ms": val}