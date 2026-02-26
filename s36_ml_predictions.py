import glob, json, csv, os
base = "evidencias_release_v3.9.11/s36"
paths = sorted(glob.glob(os.path.join(base, "01_sla_submissions", "*.json")))
out = os.path.join(base, "06_ml_predictions", "ml_predictions_raw.csv")
os.makedirs(os.path.dirname(out), exist_ok=True)

rows = []
for p in paths:
    try:
        j = json.load(open(p))
    except Exception:
        continue
    sla_id = j.get("sla_id") or j.get("decision_id") or ""
    decision = j.get("decision") or ""
    stype = (j.get("service_type") or j.get("slice_type") or "")
    ml = j.get("ml_prediction") or {}
    risk = ml.get("risk_score")
    conf = ml.get("confidence")
    model_used = ml.get("model_used")
    metrics_used = ml.get("metrics_used") or {}
    rmc = metrics_used.get("real_metrics_count")
    rows.append({
        "file": os.path.basename(p),
        "sla_id": sla_id,
        "decision": decision,
        "slice_type": stype,
        "risk_score": risk,
        "confidence": conf,
        "model_used": model_used,
        "real_metrics_count": rmc,
    })

with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["file"])
    w.writeheader()
    w.writerows(rows)

print("rows:", len(rows))
print("out:", out)
