"""Build 05_latency_tables: control_latency_raw, by_slice, by_scenario. submit_to_decision, decision_to_kafka, submit_to_kafka (ms)."""
import csv, os
from datetime import datetime

base = "evidencias_release_v3.9.11/s36_1_control_latency"
reg_path = f"{base}/01_registry/sla_registry.csv"
ts_path = f"{base}/04_timestamps/snapshot_timestamps.csv"
out_dir = f"{base}/05_latency_tables"
os.makedirs(out_dir, exist_ok=True)

def parse_utc(s):
    if not s:
        return None
    s = s.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

# registry: sla_id, slice_type, scenario, submit_timestamp_utc
reg = {}
with open(reg_path) as f:
    for row in csv.DictReader(f):
        sid = (row.get("sla_id") or "").strip()
        if not sid:
            continue
        reg[sid] = {
            "slice_type": (row.get("slice_type") or "").strip(),
            "scenario": (row.get("scenario") or "").strip(),
            "submit_timestamp_utc": (row.get("submit_timestamp_utc") or "").strip(),
        }

# timestamps: sla_id, snapshot_timestamp, decision_timestamp, kafka_timestamp
ts = {}
with open(ts_path) as f:
    for row in csv.DictReader(f):
        sid = (row.get("sla_id") or "").strip()
        if not sid:
            continue
        ts[sid] = {k: (row.get(k) or "").strip() for k in ["snapshot_timestamp", "decision_timestamp", "kafka_timestamp"]}

def delta_ms(a, b):
    ta, tb = parse_utc(a), parse_utc(b)
    if ta is None or tb is None:
        return None
    return (tb - ta).total_seconds() * 1000.0

rows = []
for sla_id, r in reg.items():
    t = ts.get(sla_id) or {}
    sub = r["submit_timestamp_utc"]
    dec = t.get("decision_timestamp") or ""
    kaf = t.get("kafka_timestamp") or ""
    submit_to_decision = delta_ms(sub, dec) if dec else None
    decision_to_kafka = delta_ms(dec, kaf) if dec and kaf else None
    submit_to_kafka = delta_ms(sub, kaf) if kaf else (submit_to_decision if submit_to_decision is not None else None)
    rows.append({
        "sla_id": sla_id,
        "slice_type": r["slice_type"],
        "scenario": r["scenario"],
        "submit_timestamp_utc": sub,
        "decision_timestamp": dec,
        "kafka_timestamp": kaf,
        "submit_to_decision_ms": "" if submit_to_decision is None else f"{submit_to_decision:.6f}",
        "decision_to_kafka_ms": "" if decision_to_kafka is None else f"{decision_to_kafka:.6f}",
        "submit_to_kafka_ms": "" if submit_to_kafka is None else f"{submit_to_kafka:.6f}",
    })

raw = f"{out_dir}/control_latency_raw.csv"
with open(raw, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print("raw:", raw, "rows:", len(rows))

# by_slice
by_slice = {}
for row in rows:
    s = row["slice_type"]
    ms = row.get("submit_to_decision_ms") or row.get("submit_to_kafka_ms")
    if ms and ms.strip():
        try:
            v = float(ms)
            by_slice.setdefault(s, []).append(v)
        except Exception:
            pass
slice_rows = []
for s, vals in sorted(by_slice.items()):
    slice_rows.append({"slice_type": s, "n": len(vals), "mean_ms": sum(vals) / len(vals), "min_ms": min(vals), "max_ms": max(vals)})
with open(f"{out_dir}/control_latency_by_slice.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["slice_type", "n", "mean_ms", "min_ms", "max_ms"])
    w.writeheader()
    w.writerows(slice_rows)

# by_scenario
by_scenario = {}
for row in rows:
    s = row["scenario"]
    ms = row.get("submit_to_decision_ms") or row.get("submit_to_kafka_ms")
    if ms and ms.strip():
        try:
            v = float(ms)
            by_scenario.setdefault(s, []).append(v)
        except Exception:
            pass
scenario_rows = []
for s, vals in sorted(by_scenario.items()):
    scenario_rows.append({"scenario": s, "n": len(vals), "mean_ms": sum(vals) / len(vals), "min_ms": min(vals), "max_ms": max(vals)})
with open(f"{out_dir}/control_latency_by_scenario.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["scenario", "n", "mean_ms", "min_ms", "max_ms"])
    w.writeheader()
    w.writerows(scenario_rows)
print("by_slice, by_scenario done.")
