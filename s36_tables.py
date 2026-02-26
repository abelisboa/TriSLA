import pandas as pd
import glob
import json
import os
base = "evidencias_release_v3.9.11/s36"
os.makedirs(f"{base}/14_tables", exist_ok=True)

reg = pd.read_csv(f"{base}/01_sla_submissions/sla_registry.csv")
sc = reg.groupby(["scenario", "slice_type"]).size().reset_index(name="n")
sc.to_csv(f"{base}/14_tables/scenario_summary.csv", index=False)

rows = []
for p in glob.glob(f"{base}/01_sla_submissions/*.json"):
    try:
        j = json.load(open(p))
    except Exception:
        continue
    sid = j.get("sla_id") or j.get("decision_id") or ""
    rows.append({"sla_id": sid, "decision": j.get("decision", "")})
dec = pd.DataFrame(rows)
reg2 = reg.merge(dec, on="sla_id", how="left")
rates = reg2.groupby(["scenario", "slice_type", "decision"]).size().reset_index(name="n")
rates.to_csv(f"{base}/14_tables/decision_rates.csv", index=False)

kv = pd.read_csv(f"{base}/08_kafka/events_validation.csv")
kvsum = kv.groupby(["valid"]).size().reset_index(name="n")
kvsum.to_csv(f"{base}/14_tables/kafka_validation_summary.csv", index=False)

print("OK tables generated.")
