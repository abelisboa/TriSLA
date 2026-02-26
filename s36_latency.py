import re, csv, os, datetime
base = "evidencias_release_v3.9.11/s36"
pb = os.path.join(base, "02_portal_backend_logs", "portal_backend.log")
de = os.path.join(base, "04_decision_engine_snapshots", "decision_engine.log")
out = os.path.join(base, "13_latency", "latency_attempt.csv")
os.makedirs(os.path.dirname(out), exist_ok=True)
iso = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)")

submit_ts = {}
if os.path.exists(pb):
    for line in open(pb, errors="ignore"):
        m = iso.search(line)
        if not m:
            continue
        if "/sla/submit" in line or "sla/submit" in line:
            t = m.group(1)
            sid = re.search(r"(dec-[a-f0-9\-]{8,})", line)
            if sid:
                submit_ts[sid.group(1)] = t

decision_ts = {}
if os.path.exists(de):
    for line in open(de, errors="ignore"):
        m = iso.search(line)
        if not m:
            continue
        if "decision" in line.lower():
            t = m.group(1)
            sid = re.search(r"(dec-[a-f0-9\-]{8,})", line)
            if sid and sid.group(1) not in decision_ts:
                decision_ts[sid.group(1)] = t

def parse(t):
    return datetime.datetime.fromisoformat(t.replace("Z", "+00:00"))

rows = []
for sid, ts in submit_ts.items():
    if sid in decision_ts:
        a = parse(ts)
        b = parse(decision_ts[sid])
        ms = (b - a).total_seconds() * 1000.0
        rows.append({"sla_id": sid, "t_submit": ts, "t_decision": decision_ts[sid], "delta_ms": ms})

with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["sla_id", "t_submit", "t_decision", "delta_ms"])
    w.writeheader()
    w.writerows(rows)

print("matched:", len(rows))
print("out:", out)
