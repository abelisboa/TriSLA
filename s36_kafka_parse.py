import json, csv, os
base = "evidencias_release_v3.9.11/s36/08_kafka"
raw = os.path.join(base, "events_raw.log")
out_json = os.path.join(base, "events_parsed.json")
out_csv = os.path.join(base, "events_validation.csv")
os.makedirs(base, exist_ok=True)

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

def has_nested(e, path):
    cur = e
    for p in path.split("."):
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return False
    return True

required = ["sla_id", "decision", "slice_type", "timestamp_utc"]
nested = ["snapshot.domains", "snapshot.bottleneck_domain", "explanation.type", "explanation.text"]
rows = []
for e in events:
    ok = True
    missing = []
    for k in required:
        if k not in e:
            ok = False
            missing.append(k)
    for n in nested:
        if not has_nested(e, n):
            ok = False
            missing.append(n)
    rows.append({
        "sla_id": e.get("sla_id", ""),
        "decision": e.get("decision", ""),
        "slice_type": e.get("slice_type", ""),
        "timestamp_utc": e.get("timestamp_utc", ""),
        "valid": "YES" if ok else "NO",
        "missing": ";".join(missing),
    })

with open(out_csv, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["sla_id", "decision", "slice_type", "timestamp_utc", "valid", "missing"])
    w.writeheader()
    w.writerows(rows)

print("events:", len(events))
print("valid:", sum(1 for r in rows if r["valid"] == "YES"))
