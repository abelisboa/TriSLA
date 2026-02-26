"""Build 04_timestamps/snapshot_timestamps.csv from registry + snapshots. Kafka ts empty if no events."""
import csv, json, os, glob
base = "evidencias_release_v3.9.11/s36_1_control_latency"
reg_path = f"{base}/01_registry/sla_registry.csv"
snap_dir = f"{base}/03_snapshots"
out_dir = f"{base}/04_timestamps"
os.makedirs(out_dir, exist_ok=True)
out = f"{out_dir}/snapshot_timestamps.csv"

# registry: sla_id, intent_id, slice_type, scenario, submit_timestamp_utc
submit_ts = {}
with open(reg_path) as f:
    r = csv.DictReader(f)
    for row in r:
        sid = (row.get("sla_id") or "").strip()
        if not sid:
            continue
        submit_ts[sid] = (row.get("submit_timestamp_utc") or "").strip()

# uuid from dec-uuid
def uuid_of(sla_id):
    s = (sla_id or "").strip()
    if s.startswith("dec-"):
        return s[4:]
    return s

# decision_<uuid>.json -> timestamp_utc
def decision_ts_of(uuid):
    p = os.path.join(snap_dir, f"decision_{uuid}.json")
    if not os.path.exists(p):
        return ""
    try:
        j = json.load(open(p))
        return (j.get("timestamp_utc") or "").strip()
    except Exception:
        return ""

# kafka: we have events_parsed.csv; map sla_id -> timestamp_utc. If empty, all kafka_ts blank.
kafka_ts = {}
parsed = os.path.join(base, "02_kafka", "events_parsed.csv")
if os.path.exists(parsed):
    with open(parsed) as f:
        r = csv.DictReader(f)
        for row in r:
            sid = (row.get("sla_id") or "").strip()
            t = (row.get("timestamp_utc") or "").strip()
            if sid and t:
                kafka_ts[sid] = t

rows = []
for sla_id, sub_ts in submit_ts.items():
    u = uuid_of(sla_id)
    dec_ts = decision_ts_of(u)
    kts = kafka_ts.get(sla_id) or kafka_ts.get(f"dec-{u}") or ""
    rows.append({
        "sla_id": sla_id,
        "snapshot_timestamp": dec_ts,
        "decision_timestamp": dec_ts,
        "kafka_timestamp": kts,
    })

with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["sla_id", "snapshot_timestamp", "decision_timestamp", "kafka_timestamp"])
    w.writeheader()
    w.writerows(rows)
print("rows:", len(rows), "out:", out)
