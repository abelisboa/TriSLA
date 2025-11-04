#!/usr/bin/env python3
import json, time, os
LOG_DIR = "./data/logs"
os.makedirs(LOG_DIR, exist_ok=True)
def write_log(module, metric, slo, decision, explanation):
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "traceId": f"{int(time.time()*1000)}",
        "module": module,
        "metric": metric,
        "slo": slo,
        "decision": decision,
        "explanation": explanation
    }
    with open(f"{LOG_DIR}/trisla_exec_{int(time.time())}.json","w", encoding='utf-8') as f:
        json.dump(entry, f, indent=2)
    print("Log registrado:", entry)

