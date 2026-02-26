#!/usr/bin/env python3
"""FASE 9 diag summary. Usage: RUN=path python3 s36_2a_diag.py"""
import re, pathlib, json, os
run = pathlib.Path(os.environ.get("RUN", ""))
if not run:
    raise SystemExit("RUN env not set")

def read(p):
    try:
        return (run / p).read_text(errors="ignore")
    except Exception:
        return ""

before = read("08_submit_probe/offsets_before.txt")
after = read("08_submit_probe/offsets_after.txt")

def parse_offsets(txt):
    m = re.findall(r"trisla-decision-events:(\d+):(\d+)", txt)
    return {int(p): int(o) for p, o in m}

ob = parse_offsets(before)
oa = parse_offsets(after)
producer_ok = bool(ob and oa and any(oa.get(k, 0) > ob.get(k, 0) for k in oa))
topic_has_data = bool(oa and any(v > 0 for v in oa.values()))

cg_desc = read("05_consumer/consumer_groups_describe_s36-latency-audit.txt")
coordinator_ok = "FIND_COORDINATOR" not in cg_desc and "Timeout" not in cg_desc and "TimeoutException" not in cg_desc

dns_tcp = read("07_network/dns_tcp_checks.txt")
dns_ok = ("OK kafka 9092" in dns_tcp) or ("OK kafka.trisla.svc.cluster.local 9092" in dns_tcp)

summary = {
    "producer_ok_by_offset_delta": producer_ok,
    "topic_has_data_by_offsets": topic_has_data,
    "consumer_group_coordinator_ok": coordinator_ok,
    "dns_tcp_ok": dns_ok,
}
out = run / "09_analysis" / "diag_summary.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
