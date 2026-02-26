"""FASE 6: Correlate submit_*.json, decision_*.json (S30), Kafka events -> 06_correlation/correlation_matrix.csv."""
import json, csv, os
from datetime import datetime

base = "evidencias_release_v3.9.11/s36_2_kafka_fix"
submit_dir = os.path.join(base, "03_submit")
snap_dir = "evidencias_release_v3.9.11/s36_1_control_latency/03_snapshots"
parsed = os.path.join(base, "05_validation", "events_parsed.json")
out_dir = os.path.join(base, "06_correlation")
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "correlation_matrix.csv")

def parse_utc(s):
    if not s:
        return None
    s = str(s).strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

def uuid_of(sla_id):
    s = (sla_id or "").strip()
    if s.startswith("dec-"):
        return s[4:]
    return s

# 03_submit: submit_A/B/C.json -> sla_id, submit_ts (we need submit time; use mtime or embed)
# We didn't embed submit_ts in S36.2. Use file mtime as proxy, or parse created_at from JSON if present.
submit_info = {}
for name in ["submit_A", "submit_B", "submit_C"]:
    p = os.path.join(submit_dir, f"{name}.json")
    if not os.path.exists(p):
        continue
    try:
        j = json.load(open(p))
        sid = j.get("sla_id") or j.get("decision_id") or ""
        if not sid:
            continue
        ts = (j.get("created_at") or j.get("timestamp") or j.get("submit_timestamp_utc") or "").strip()
        if not ts:
            ts = datetime.utcfromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%dT%H:%M:%SZ")
        submit_info[sid] = {"scenario": name.replace("submit_", ""), "submit_ts": ts}
    except Exception:
        pass

# Snapshots: decision_<uuid>.json -> timestamp_utc (06_correlation, then s36_1 03_snapshots)
def decision_ts_of(sla_id):
    u = uuid_of(sla_id)
    for d in [os.path.join(base, "06_correlation"), snap_dir, os.path.join(base, "03_snapshots")]:
        p = os.path.join(d, f"decision_{u}.json")
        if os.path.exists(p):
            try:
                j = json.load(open(p))
                return (j.get("timestamp_utc") or "").strip()
            except Exception:
                pass
    return ""

# Kafka events: sla_id -> timestamp_utc
kafka_ts = {}
if os.path.exists(parsed):
    try:
        for e in json.load(open(parsed)):
            sid = e.get("sla_id") or e.get("decision_id") or ""
            t = (e.get("timestamp_utc") or "").strip()
            if sid and t:
                kafka_ts[sid] = t
    except Exception:
        pass

def delta_ms(a, b):
    ta, tb = parse_utc(a), parse_utc(b)
    if ta is None or tb is None:
        return None
    return (tb - ta).total_seconds() * 1000.0

rows = []
for sla_id, info in submit_info.items():
    sub_ts = info["submit_ts"]
    dec_ts = decision_ts_of(sla_id)
    kts = kafka_ts.get(sla_id) or ""
    d_sk = delta_ms(sub_ts, kts) if kts else None
    d_kd = delta_ms(kts, dec_ts) if kts and dec_ts else None
    rows.append({
        "sla_id": sla_id,
        "submit_ts": sub_ts,
        "decision_ts": dec_ts,
        "kafka_ts": kts,
        "delta_submit_kafka_ms": "" if d_sk is None else f"{d_sk:.6f}",
        "delta_kafka_decision_ms": "" if d_kd is None else f"{d_kd:.6f}",
    })

with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["sla_id", "submit_ts", "decision_ts", "kafka_ts", "delta_submit_kafka_ms", "delta_kafka_decision_ms"])
    w.writeheader()
    w.writerows(rows)
print("correlation rows:", len(rows), "out:", out)
