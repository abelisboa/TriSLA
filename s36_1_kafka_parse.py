"""Parse Kafka events_raw.log -> events_parsed.json, events_parsed.csv. Fields: sla_id, decision, slice_type, timestamp_utc, snapshot.bottleneck_domain, explanation.type."""
import json, csv, os
base = "evidencias_release_v3.9.11/s36_1_control_latency/02_kafka"
raw = os.path.join(base, "events_raw.log")
out_json = os.path.join(base, "events_parsed.json")
out_csv = os.path.join(base, "events_parsed.csv")
events = []
if os.path.exists(raw):
    for line in open(raw, encoding="utf-8", errors="ignore"):
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except Exception:
            pass
json.dump(events, open(out_json, "w"), indent=2)
rows = []
for e in events:
    snap = e.get("snapshot") or {}
    expl = e.get("explanation") or {}
    rows.append({
        "sla_id": e.get("sla_id", ""),
        "decision": e.get("decision", ""),
        "slice_type": e.get("slice_type", ""),
        "timestamp_utc": e.get("timestamp_utc", ""),
        "bottleneck_domain": snap.get("bottleneck_domain", ""),
        "explanation_type": expl.get("type", ""),
    })
with open(out_csv, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["sla_id", "decision", "slice_type", "timestamp_utc", "bottleneck_domain", "explanation_type"])
    w.writeheader()
    w.writerows(rows)
print("events:", len(events))
