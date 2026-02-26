"""FASE 5: Parse 04_events_after_submit.log -> events_parsed.json, events_validation.csv. Fields: sla_id, decision, slice_type, timestamp_utc, snapshot, explanation."""
import json, csv, os
base = "evidencias_release_v3.9.11/s36_2_kafka_fix"
raw = os.path.join(base, "04_events_after_submit.log")
out_json = os.path.join(base, "05_validation", "events_parsed.json")
out_csv = os.path.join(base, "05_validation", "events_validation.csv")
os.makedirs(os.path.dirname(out_json), exist_ok=True)
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
    snap = e.get("snapshot") if isinstance(e.get("snapshot"), dict) else {}
    expl = e.get("explanation") if isinstance(e.get("explanation"), dict) else {}
    has_snap = "snapshot" in e and isinstance(e["snapshot"], dict)
    has_expl = "explanation" in e and isinstance(e["explanation"], dict)
    rows.append({
        "sla_id": e.get("sla_id") or e.get("decision_id") or "",
        "decision": e.get("decision") or e.get("action") or "",
        "slice_type": e.get("slice_type") or "",
        "timestamp_utc": e.get("timestamp_utc") or "",
        "has_snapshot": "YES" if has_snap else "NO",
        "has_explanation": "YES" if has_expl else "NO",
    })
with open(out_csv, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["sla_id", "decision", "slice_type", "timestamp_utc", "has_snapshot", "has_explanation"])
    w.writeheader()
    w.writerows(rows)
print("events:", len(events))
