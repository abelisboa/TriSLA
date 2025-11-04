import random, time, json, requests

def generate_nwdaf_metrics():
    return {
        "nsiId": f"nsi-{random.randint(100,999)}",
        "riskScore": round(random.uniform(0.0, 1.0), 2),
        "features": {"utilization": round(random.uniform(0.5,0.9),2), "latencyP95": random.randint(10,120)}
    }

def push_to_nasp(data):
    requests.post("http://nasp.local/v1/nasp/telemetry", json=data, timeout=2)

if __name__ == "__main__":
    while True:
        d = generate_nwdaf_metrics()
        print("[NWDAF] ->", json.dumps(d))
        push_to_nasp(d)
        time.sleep(10)

