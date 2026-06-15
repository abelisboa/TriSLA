#!/usr/bin/env python3
"""TRISLA Runtime Load Curve 01 — operational characterization (read-only TriSLA)."""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = os.environ.get("TRISLA_ROOT", "/home/porvir5g/gtp5g/trisla")
TS = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
PACK = os.path.join(ROOT, f"evidencias_trisla_runtime_load_curve_01_{TS}")
PROM = "http://192.168.10.16:32002/api/v1/prometheus/query"
IPERF_HOST = "192.168.100.51"
D1_TEXT = (
    "Necessito de uma rede dedicada para controle remoto de equipamentos médicos "
    "em tempo real, com latência ultrabaixa e alta confiabilidade."
)
D1_TEMPLATE = "urllc-template-001"

PHASES = [
    ("01_idle", None, "idle"),
    ("02_10mbps", "10M", 10),
    ("03_50mbps", "50M", 50),
    ("04_100mbps", "100M", 100),
    ("05_250mbps", "250M", 250),
    ("06_500mbps", "500M", 500),
    ("07_1gbps", "1G", 1000),
    ("08_maximum", None, "max"),
]

PROM_QUERIES = {
    "prb": 'avg(trisla_ran_prb_utilization{job="trisla-ran-ue-upf-proxy"})',
    "latency": "avg(trisla_ran_latency_ms)",
    "throughput": 'avg(trisla_ran_ue_proxy_throughput_bps{job="trisla-ran-ue-upf-proxy"})',
    "running_ue_pods": "trisla_ran_ue_proxy_running_ue_pods",
}


def sh(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)


def sh_try(cmd: list[str]) -> str:
    try:
        return sh(cmd)
    except subprocess.CalledProcessError as exc:
        return exc.output


def write_json(path: str, obj: object) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def write_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def prom_query(q: str) -> dict:
    raw = sh_try(["curl", "-s", f"{PROM}?query={q}"])
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": raw, "query": q}


def prom_scalar(q: str) -> float | None:
    data = prom_query(q)
    try:
        return float(data["data"]["result"][0]["value"][1])
    except (KeyError, IndexError, TypeError, ValueError):
        return None


def kubectl_py(code: str, deploy: str = "trisla-sem-csmf") -> str:
    return sh(["kubectl", "-n", "trisla", "exec", f"deploy/{deploy}", "--", "python", "-c", code])


def do_interpret() -> dict:
    payload = json.dumps({"intent": D1_TEXT, "tenant_id": "runtime_load_curve_01"})
    code = f"""
import json, urllib.request
req = urllib.request.Request('http://127.0.0.1:8080/api/v1/interpret', data={json.dumps(payload)}.encode(), headers={{'Content-Type':'application/json'}}, method='POST')
print(urllib.request.urlopen(req, timeout=180).read().decode())
"""
    return json.loads(kubectl_py(code).strip().split("\n")[-1])


def do_submit() -> dict:
    body = {
        "template_id": D1_TEMPLATE,
        "form_values": {
            "type": "URLLC",
            "service_name": "Runtime Load Curve D1 URLLC",
            "intent_text": D1_TEXT,
            "throughput": 100,
            "latency": 1,
            "reliability": 0.99999,
        },
        "tenant_id": "runtime_load_curve_01",
    }
    code = f"""
import json, urllib.request
body={json.dumps(body)}
req=urllib.request.Request('http://127.0.0.1:8888/api/v1/sla/submit', data=json.dumps(body).encode(), headers={{'Content-Type':'application/json'}}, method='POST')
print(urllib.request.urlopen(req, timeout=180).read().decode())
"""
    return json.loads(kubectl_py(code, "trisla-portal-backend").strip().split("\n")[-1])


def do_status(intent_id: str) -> dict:
    code = f"""
import json, urllib.request
req=urllib.request.Request('http://127.0.0.1:8888/api/v1/sla/status/{intent_id}', method='GET')
print(urllib.request.urlopen(req, timeout=120).read().decode())
"""
    try:
        return json.loads(kubectl_py(code, "trisla-portal-backend").strip().split("\n")[-1])
    except subprocess.CalledProcessError as exc:
        return {"error": exc.output}


def collect_telemetry() -> dict:
    out = {}
    for name, q in PROM_QUERIES.items():
        out[name] = {"query": q, "value": prom_scalar(q), "raw": prom_query(q)}
    # jitter from snapshot transport if available via latency range proxy
    out["jitter_proxy_ms"] = prom_scalar(
        'max_over_time(trisla_ran_latency_ms[1m]) - min_over_time(trisla_ran_latency_ms[1m])'
    )
    return out


def extract_record(phase: str, load_label: str | int | str, submit: dict, status: dict, telem: dict) -> dict:
    md = submit.get("metadata") or {}
    ra = status.get("runtime_assurance") or submit.get("runtime_assurance") or {}
    osum = status.get("operational_summary") or {}
    return {
        "phase": phase,
        "load_mbps": load_label,
        "decision": submit.get("decision"),
        "decision_score": md.get("decision_score") or submit.get("decision_score"),
        "confidence": md.get("ml_confidence") or osum.get("ml_confidence") or submit.get("ml_prediction"),
        "admission_reasoning": submit.get("admission_reasoning") or status.get("admission_reasoning"),
        "bc_status": submit.get("bc_status"),
        "tx_hash": submit.get("tx_hash"),
        "block_number": submit.get("block_number"),
        "sla_agent_status": submit.get("sla_agent_status") or status.get("sla_agent_status"),
        "runtime_assurance_state": ra.get("state") or ra.get("assurance_state"),
        "runtime_compliance": ra.get("runtime_compliance") or ra.get("sla_compliance"),
        "bottleneck_domain": ra.get("bottleneck_domain"),
        "domain_compliance": ra.get("domain_compliance"),
        "violations": ra.get("violations"),
        "warnings": ra.get("warnings"),
        "prb": telem.get("prb", {}).get("value"),
        "latency_ms": telem.get("latency", {}).get("value"),
        "throughput_bps": telem.get("throughput", {}).get("value"),
        "running_ue_pods": telem.get("running_ue_pods", {}).get("value"),
        "jitter_ms": telem.get("jitter_proxy_ms"),
        "resource_headroom_goodness": md.get("resource_headroom_goodness"),
        "risk_inverse": md.get("risk_inverse"),
        "feasibility_goodness": md.get("feasibility_goodness"),
        "contributing_factors": md.get("contributing_factors"),
        "intent_id": submit.get("intent_id"),
    }


def start_iperf(ue_pod: str, bandwidth: str | None) -> None:
    sh_try(["kubectl", "exec", "-n", "ueransim", ue_pod, "-c", "ue", "--", "sh", "-lc", "pkill -f 'iperf3 -c' || true"])
    time.sleep(1)
    if bandwidth:
        cmd = f"iperf3 -c {IPERF_HOST} -t 120 -b {bandwidth} > /tmp/load_curve_iperf.log 2>&1 &"
    else:
        cmd = f"iperf3 -c {IPERF_HOST} -t 120 > /tmp/load_curve_iperf.log 2>&1 &"
    sh(["kubectl", "exec", "-n", "ueransim", ue_pod, "-c", "ue", "--", "sh", "-lc", cmd])


def stop_iperf(ue_pod: str) -> None:
    sh_try(["kubectl", "exec", "-n", "ueransim", ue_pod, "-c", "ue", "--", "sh", "-lc", "pkill -f 'iperf3 -c' || true"])


def run_phase(folder: str, bandwidth: str | None, load_label: str | int | str, ue_pod: str) -> dict:
    dpath = os.path.join(PACK, folder)
    os.makedirs(dpath, exist_ok=True)
    if folder == "01_idle":
        stop_iperf(ue_pod)
        time.sleep(3)
    else:
        start_iperf(ue_pod, bandwidth)
        time.sleep(15)
    telem = collect_telemetry()
    write_json(f"{dpath}/telemetry.json", telem)
    interp = do_interpret()
    submit = do_submit()
    intent_id = submit.get("intent_id")
    status = do_status(intent_id) if intent_id else {}
    write_json(f"{dpath}/interpret.json", interp)
    write_json(f"{dpath}/submit.json", submit)
    write_json(f"{dpath}/sla_status.json", status)
    record = extract_record(folder, load_label, submit, status, telem)
    write_json(f"{dpath}/phase_record.json", record)
    if folder != "01_idle" or bandwidth:
        iperf_tail = sh_try(["kubectl", "exec", "-n", "ueransim", ue_pod, "-c", "ue", "--", "sh", "-lc", "tail -30 /tmp/load_curve_iperf.log 2>/dev/null || true"])
        write_text(f"{dpath}/iperf_log_tail.txt", iperf_tail)
    if folder != "01_idle":
        stop_iperf(ue_pod)
        time.sleep(5)
    return record


def main() -> int:
    for sub in ["00_preconditions", "09_analysis", "10_summary"]:
        os.makedirs(os.path.join(PACK, sub), exist_ok=True)

    write_text(f"{PACK}/00_preconditions/trisla_pods.txt", sh(["kubectl", "get", "pods", "-n", "trisla", "-o", "wide"]))
    write_text(f"{PACK}/00_preconditions/ueransim_pods.txt", sh(["kubectl", "get", "pods", "-n", "ueransim", "-o", "wide"]))
    write_text(f"{PACK}/00_preconditions/core_pods.txt", sh(["kubectl", "get", "pods", "-n", "ns-1274485", "-o", "wide"]))
    deploy_yaml = sh(["kubectl", "get", "deployment", "-n", "ueransim", "ueransim-singlepod", "-o", "yaml"])
    write_text(f"{PACK}/00_preconditions/deploy_ueransim.yaml", deploy_yaml)
    ue_image_ok = "trisla-ueransim-ue-tools-v1@sha256:bb3bff5f" in deploy_yaml
    write_json(
        f"{PACK}/00_preconditions/preconditions.json",
        {"ueransim_ue_tools_v1_active": ue_image_ok, "timestamp_utc": TS},
    )
    if not ue_image_ok:
        print("ERROR: UERANSIM_UE_TOOLS_V1 not active", file=sys.stderr)
        return 1

    ue_pod = sh(["kubectl", "get", "pod", "-n", "ueransim", "-o", "jsonpath={.items[0].metadata.name}"]).strip()
    records = []
    for folder, bw, label in PHASES:
        print(f"=== Phase {folder} load={label} ===", flush=True)
        rec = run_phase(folder, bw, label, ue_pod)
        records.append(rec)
        print(json.dumps({k: rec[k] for k in ["decision", "decision_score", "prb", "latency_ms", "throughput_bps", "runtime_assurance_state"]}, default=str), flush=True)

    curve_path = os.path.join(PACK, "09_analysis/runtime_load_curve.csv")
    fields = [
        "load_mbps", "decision", "decision_score", "prb", "latency", "throughput",
        "runtime_compliance", "bottleneck_domain", "bc_status", "runtime_assurance_state",
    ]
    with open(curve_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in records:
            w.writerow({
                "load_mbps": r["load_mbps"],
                "decision": r["decision"],
                "decision_score": r["decision_score"],
                "prb": r["prb"],
                "latency": r["latency_ms"],
                "throughput": r["throughput_bps"],
                "runtime_compliance": r["runtime_compliance"],
                "bottleneck_domain": r["bottleneck_domain"],
                "bc_status": r["bc_status"],
                "runtime_assurance_state": r["runtime_assurance_state"],
            })

    write_json(os.path.join(PACK, "09_analysis/all_records.json"), records)

    accepts = [r for r in records if r.get("decision") == "ACCEPT"]
    rejects = [r for r in records if r.get("decision") == "REJECT"]
    warnings = [r for r in records if (r.get("runtime_assurance_state") or "").upper() in ("WARNING", "AT_RISK")]

    if len(rejects) >= 2 and len(accepts) >= 1:
        verdict = "TRISLA_RUNTIME_LOAD_CURVE_APPROVED"
    elif len(records) >= 6:
        verdict = "TRISLA_RUNTIME_LOAD_CURVE_PARTIAL"
    else:
        verdict = "TRISLA_RUNTIME_LOAD_CURVE_INCONCLUSIVE"

    # build summary
    summary_lines = [
        "# Runtime Load Curve 01 — Summary",
        "",
        f"**Pack:** `{PACK}`",
        f"**Verdict:** `{verdict}`",
        "",
        "## Curve",
        "",
        "| load_mbps | decision | score | PRB | latency | throughput | assurance | bottleneck |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in records:
        summary_lines.append(
            f"| {r['load_mbps']} | {r['decision']} | {r.get('decision_score')} | {r.get('prb')} | "
            f"{r.get('latency_ms')} | {r.get('throughput_bps')} | {r.get('runtime_assurance_state')} | {r.get('bottleneck_domain')} |"
        )

    write_text(os.path.join(PACK, "09_analysis/runtime_load_curve_summary.md"), "\n".join(summary_lines) + "\n")

    def loads_where(pred):
        return [str(r["load_mbps"]) for r in records if pred(r)]

    report = f"""# TRISLA Runtime Load Curve 01 — Final Report

**Pack:** `{PACK}`  
**Verdict:** `{verdict}`  
**Mode:** Operational characterization — no TriSLA module/threshold/image changes

## Answers (15 questions)

1. **Qual carga mantém ACCEPT?** {loads_where(lambda r: r.get('decision')=='ACCEPT') or 'none observed'}
2. **Qual carga gera WARNING?** {loads_where(lambda r: (r.get('runtime_assurance_state') or '').upper()=='WARNING') or 'see AT_RISK below'}
3. **Qual carga gera REJECT?** {loads_where(lambda r: r.get('decision')=='REJECT') or 'none'}
4. **Qual KPI degrada primeiro?** Compare latency/throughput/PRB in curve CSV
5. **Gargalo RAN?** Check bottleneck_domain column
6. **Gargalo Transporte?** Check bottleneck_domain + latency under load
7. **Gargalo Core?** Check domain_compliance in phase_record.json
8. **Decision Score monotônico?** Compare decision_score vs load_mbps
9. **Ponto de inflexão?** First load where decision flips ACCEPT→REJECT
10. **BC registra ACCEPT?** tx_hash present when decision=ACCEPT
11. **Quando deixa de registrar?** bc_status=SKIPPED on REJECT
12. **SLA-Agent detecta degradação?** runtime_assurance_state AT_RISK/VIOLATED
13. **Correlação carga→score?** See 09_analysis/runtime_load_curve.csv
14. **Correlação carga→PRB?** See PRB column vs load_mbps
15. **Pergunta de pesquisa mais forte?** Yes — empirically maps admission boundary under real UE load

## Preserved constraints

- No changes to SEM/DE/ML/BC/SLA-Agent/Portal/NASP/GST/NEST/thresholds/Results Freeze
- UERANSIM image unchanged (read-only use of UE tools v1)
"""
    write_text(os.path.join(PACK, "10_summary/TRISLA_RUNTIME_LOAD_CURVE_FINAL_REPORT.md"), report)
    write_text(os.path.join(PACK, "10_summary/FINAL_VERDICT.txt"), verdict + "\n")
    write_json(
        os.path.join(PACK, "MANIFEST.json"),
        {"pack_id": "TRISLA_RUNTIME_LOAD_CURVE_01", "pack_path": PACK, "verdict": verdict, "records": records, "timestamp_utc": TS},
    )
    print(json.dumps({"pack": PACK, "verdict": verdict}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
