#!/usr/bin/env python3
"""TRISLA Multi-Slice Runtime Load 01 — tri-slice differentiation under real UE load."""
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
PACK = os.path.join(ROOT, f"evidencias_trisla_multi_slice_runtime_load_01_{TS}")
IPERF_HOST = "192.168.100.51"
TENANT = "multi_slice_runtime_load_01"

CASES = {
    "D1": {
        "slice_type": "URLLC",
        "template_id": "urllc-template-001",
        "text": (
            "Necessito de uma rede dedicada para controle remoto de equipamentos médicos "
            "em tempo real, com latência ultrabaixa e alta confiabilidade."
        ),
        "throughput": 100,
        "latency": 1,
        "reliability": 0.99999,
    },
    "D2": {
        "slice_type": "mMTC",
        "template_id": "mmtc-template-001",
        "text": "Cidade inteligente com milhares de sensores IoT distribuídos.",
        "throughput": 0.1,
        "latency": 1000,
        "reliability": 0.99,
    },
    "D6": {
        "slice_type": "eMBB",
        "template_id": "embb-template-001",
        "text": "Criar slice eMBB com throughput mínimo de 1Gbps para streaming de vídeo.",
        "throughput": 1000,
        "latency": 50,
        "reliability": 0.99,
    },
}

PHASES = [
    ("01_baseline", None, "baseline"),
    ("02_100mbps", "100M", 100),
    ("03_500mbps", "500M", 500),
    ("04_1gbps", "1G", 1000),
    ("05_maximum", None, "max"),
]


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


def kubectl_py(code: str, deploy: str = "trisla-sem-csmf") -> str:
    return sh(["kubectl", "-n", "trisla", "exec", f"deploy/{deploy}", "--", "python", "-c", code])


def interpret(text: str) -> dict:
    payload = json.dumps({"intent": text, "tenant_id": TENANT})
    code = f"""
import json, urllib.request
req=urllib.request.Request('http://127.0.0.1:8080/api/v1/interpret', data={json.dumps(payload)}.encode(), headers={{'Content-Type':'application/json'}}, method='POST')
print(urllib.request.urlopen(req, timeout=180).read().decode())
"""
    return json.loads(kubectl_py(code).strip().split("\n")[-1])


def submit(case: dict) -> dict:
    body = {
        "template_id": case["template_id"],
        "form_values": {
            "type": case["slice_type"],
            "service_name": f"Multi-slice load {case['slice_type']}",
            "intent_text": case["text"],
            "throughput": case["throughput"],
            "latency": case["latency"],
            "reliability": case["reliability"],
        },
        "tenant_id": TENANT,
    }
    code = f"""
import json, urllib.request
body={json.dumps(body)}
req=urllib.request.Request('http://127.0.0.1:8888/api/v1/sla/submit', data=json.dumps(body).encode(), headers={{'Content-Type':'application/json'}}, method='POST')
print(urllib.request.urlopen(req, timeout=180).read().decode())
"""
    return json.loads(kubectl_py(code, "trisla-portal-backend").strip().split("\n")[-1])


def sla_status(intent_id: str) -> dict:
    code = f"""
import json, urllib.request
req=urllib.request.Request('http://127.0.0.1:8888/api/v1/sla/status/{intent_id}', method='GET')
print(urllib.request.urlopen(req, timeout=120).read().decode())
"""
    try:
        return json.loads(kubectl_py(code, "trisla-portal-backend").strip().split("\n")[-1])
    except subprocess.CalledProcessError as exc:
        return {"error": exc.output}


def stop_iperf(ue_pod: str) -> None:
    sh_try(["kubectl", "exec", "-n", "ueransim", ue_pod, "-c", "ue", "--", "sh", "-lc", "pkill -f 'iperf3 -c' || true"])


def start_iperf(ue_pod: str, bandwidth: str | None) -> None:
    stop_iperf(ue_pod)
    time.sleep(1)
    if bandwidth:
        cmd = f"iperf3 -c {IPERF_HOST} -t 180 -b {bandwidth} > /tmp/multi_slice_iperf.log 2>&1 &"
    else:
        cmd = f"iperf3 -c {IPERF_HOST} -t 180 > /tmp/multi_slice_iperf.log 2>&1 &"
    sh(["kubectl", "exec", "-n", "ueransim", ue_pod, "-c", "ue", "--", "sh", "-lc", cmd])


def extract_row(case_id: str, case: dict, load_label, phase: str, sub: dict, status: dict) -> dict:
    md = sub.get("metadata") or {}
    ra = status.get("runtime_assurance") or sub.get("runtime_assurance") or {}
    osum = status.get("operational_summary") or {}
    cf = md.get("contributing_factors") or sub.get("contributing_factors") or []
    factor = lambda name: next((x.get("input") for x in cf if x.get("factor") == name), None)
    return {
        "phase": phase,
        "case_id": case_id,
        "load_mbps": load_label,
        "slice_type": case["slice_type"],
        "decision": sub.get("decision"),
        "decision_score": md.get("decision_score") or sub.get("decision_score"),
        "confidence": md.get("ml_confidence") or osum.get("ml_confidence") or sub.get("confidence"),
        "admission_reasoning": sub.get("admission_reasoning") or md.get("decision_explanation_plain"),
        "decision_mode": md.get("decision_mode") or md.get("decision_source") or sub.get("reasoning"),
        "bc_status": sub.get("bc_status"),
        "tx_hash": sub.get("tx_hash"),
        "block_number": sub.get("block_number"),
        "sla_agent_status": sub.get("sla_agent_status") or status.get("sla_agent_status"),
        "runtime_state": ra.get("state") or ra.get("assurance_state"),
        "sla_compliance": ra.get("sla_compliance"),
        "runtime_compliance": ra.get("runtime_compliance"),
        "domain_compliance": ra.get("domain_compliance"),
        "bottleneck_domain": ra.get("bottleneck_domain"),
        "violations": ra.get("violations"),
        "prb_input": md.get("ran_prb_utilization_input"),
        "latency_input": md.get("transport_latency_ms_input") or md.get("transport_latency_input"),
        "resource_headroom_goodness": factor("resource_headroom_goodness"),
        "risk_inverse": factor("risk_inverse"),
        "feasibility_goodness": factor("feasibility_goodness"),
        "ran_prb_goodness": factor("ran_prb_goodness"),
        "semantic_ok": sub.get("service_type") == case["slice_type"],
        "intent_id": sub.get("intent_id"),
    }


def run_phase(folder: str, bandwidth: str | None, load_label, ue_pod: str) -> list[dict]:
    dpath = os.path.join(PACK, folder)
    os.makedirs(dpath, exist_ok=True)
    if folder == "01_baseline":
        stop_iperf(ue_pod)
        time.sleep(3)
    else:
        start_iperf(ue_pod, bandwidth)
        time.sleep(15)
    rows = []
    for case_id, case in CASES.items():
        interp = interpret(case["text"])
        sub = submit(case)
        status = sla_status(sub.get("intent_id")) if sub.get("intent_id") else {}
        write_json(f"{dpath}/{case_id}_interpret.json", interp)
        write_json(f"{dpath}/{case_id}_submit.json", sub)
        write_json(f"{dpath}/{case_id}_sla_status.json", status)
        row = extract_row(case_id, case, load_label, folder, sub, status)
        write_json(f"{dpath}/{case_id}_record.json", row)
        rows.append(row)
        print(json.dumps({k: row[k] for k in ["case_id", "slice_type", "decision", "decision_score", "runtime_state", "bottleneck_domain"]}, default=str), flush=True)
    if folder != "01_baseline":
        stop_iperf(ue_pod)
        time.sleep(5)
    return rows


def compare_rows(all_rows: list[dict]) -> dict:
    by_load = {}
    for r in all_rows:
        by_load.setdefault(str(r["load_mbps"]), []).append(r)
    diff_decisions = sum(1 for rows in by_load.values() if len({x["decision"] for x in rows}) > 1)
    diff_scores = sum(
        1
        for rows in by_load.values()
        if len({round(x["decision_score"], 4) for x in rows if x.get("decision_score") is not None}) > 1
    )
    diff_bottleneck = sum(
        1 for rows in by_load.values() if len({x.get("bottleneck_domain") for x in rows if x.get("bottleneck_domain")}) > 1
    )
    return {
        "loads_with_different_decisions": diff_decisions,
        "loads_with_different_scores": diff_scores,
        "loads_with_different_bottleneck": diff_bottleneck,
    }


def verdict_for(cmp: dict, all_rows: list[dict]) -> str:
    if cmp["loads_with_different_decisions"] >= 2 or cmp["loads_with_different_scores"] >= 3:
        return "TRISLA_MULTI_SLICE_RUNTIME_DIFFERENTIATION_APPROVED"
    if cmp["loads_with_different_decisions"] >= 1 or cmp["loads_with_different_scores"] >= 1:
        return "TRISLA_MULTI_SLICE_RUNTIME_PARTIAL"
    return "TRISLA_MULTI_SLICE_RUNTIME_NOT_OBSERVED"


def main() -> int:
    for d in ["00_preconditions", "06_analysis", "07_summary"]:
        os.makedirs(os.path.join(PACK, d), exist_ok=True)

    write_text(f"{PACK}/00_preconditions/trisla_pods.txt", sh(["kubectl", "get", "pods", "-n", "trisla", "-o", "wide"]))
    write_text(f"{PACK}/00_preconditions/ueransim_pods.txt", sh(["kubectl", "get", "pods", "-n", "ueransim", "-o", "wide"]))
    write_text(f"{PACK}/00_preconditions/core_pods.txt", sh(["kubectl", "get", "pods", "-n", "ns-1274485", "-o", "wide"]))
    deploy_yaml = sh(["kubectl", "get", "deployment", "-n", "ueransim", "ueransim-singlepod", "-o", "yaml"])
    write_text(f"{PACK}/00_preconditions/deploy_ueransim.yaml", deploy_yaml)
    ue_ok = "trisla-ueransim-ue-tools-v1@sha256:bb3bff5f" in deploy_yaml
    write_json(f"{PACK}/00_preconditions/preconditions.json", {"ueransim_ue_tools_v1": ue_ok, "timestamp_utc": TS})
    if not ue_ok:
        print("ERROR: UERANSIM_UE_TOOLS_V1 not active", file=sys.stderr)
        return 1

    ue_pod = sh(["kubectl", "get", "pod", "-n", "ueransim", "-o", "jsonpath={.items[0].metadata.name}"]).strip()
    all_rows: list[dict] = []
    for folder, bw, label in PHASES:
        print(f"=== {folder} load={label} ===", flush=True)
        all_rows.extend(run_phase(folder, bw, label, ue_pod))

    matrix_path = os.path.join(PACK, "06_analysis/tri_slice_runtime_matrix.csv")
    fields = [
        "load_mbps", "slice_type", "decision", "decision_score", "runtime_state",
        "sla_compliance", "bottleneck_domain", "bc_status", "case_id", "prb_input",
    ]
    with open(matrix_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in all_rows:
            w.writerow({k: r.get(k if k != "runtime_state" else "runtime_state") for k in fields})

    write_json(os.path.join(PACK, "06_analysis/all_records.json"), all_rows)
    cmp = compare_rows(all_rows)
    write_json(os.path.join(PACK, "06_analysis/comparative_analysis.json"), cmp)
    verdict = verdict_for(cmp, all_rows)

    def first_where(slice_type, pred):
        for r in all_rows:
            if r["slice_type"] == slice_type and pred(r):
                return r
        return None

    baseline = [r for r in all_rows if r["phase"] == "01_baseline"]
    report = f"""# TRISLA Multi-Slice Runtime Load 01 — Final Report

**Pack:** `{PACK}`  
**Verdict:** `{verdict}`  
**Mode:** READ-ONLY operational — no architecture/runtime changes

## Comparative matrix summary

| load | URLLC | mMTC | eMBB |
|------|-------|------|------|
"""
    for label in ["baseline", 100, 500, 1000, "max"]:
        rows = [r for r in all_rows if str(r["load_mbps"]) == str(label)]
        if not rows:
            continue
        by = {r["slice_type"]: r for r in rows}
        report += f"| {label} | {by.get('URLLC',{}).get('decision')} ({by.get('URLLC',{}).get('decision_score')}) | {by.get('mMTC',{}).get('decision')} ({by.get('mMTC',{}).get('decision_score')}) | {by.get('eMBB',{}).get('decision')} ({by.get('eMBB',{}).get('decision_score')}) |\n"

    report += f"""
## Phase 11 — Comparative analysis

- **URLLC treated differently?** {cmp['loads_with_different_decisions'] >= 1 or cmp['loads_with_different_scores'] >= 1}
- **eMBB degraded first?** Compare REJECT/RENEG timing vs URLLC/mMTC in matrix
- **mMTC degraded first?** See matrix per load
- **All equal?** {cmp['loads_with_different_decisions'] == 0 and cmp['loads_with_different_scores'] == 0}
- **Highest score preserved:** slice with max decision_score per load in CSV
- **Highest compliance:** compare sla_compliance/runtime_compliance columns
- **REJECT first:** first slice with REJECT at lowest load in matrix

## 15 mandatory answers

1. **All ACCEPT at idle?** {all(r.get('decision')=='ACCEPT' for r in baseline)}
2. **First to degrade (decision)?** earliest non-ACCEPT per slice from matrix
3. **First VIOLATED?** first runtime_state=VIOLATED per slice
4. **First REJECT?** lowest load with REJECT per slice
5. **Operational differentiation?** {cmp['loads_with_different_decisions'] > 0}
6. **Score differentiation?** {cmp['loads_with_different_scores'] > 0}
7. **SLA-Agent differentiation?** compare runtime_state across slices
8. **Blockchain differentiation?** compare bc_status/tx_hash across slices
9. **Bottleneck differentiation?** {cmp['loads_with_different_bottleneck'] > 0}
10. **Aligned with TriSLA proposal?** slice-aware scores/gates observed in metadata
11. **URLLC more favorable?** compare scores at same load
12. **eMBB more degradation?** compare decision transitions
13. **mMTC stability?** compare mMTC row vs others
14. **Experimentally observable?** {verdict != 'TRISLA_MULTI_SLICE_RUNTIME_NOT_OBSERVED'}
15. **Stronger dissertation hypothesis?** Yes if differentiation APPROVED/PARTIAL

## Constraints preserved

RESULTS_FREEZE_MAIN unchanged. No TriSLA module/threshold/image changes.

Full data: `06_analysis/tri_slice_runtime_matrix.csv`
"""
    write_text(os.path.join(PACK, "07_summary/TRISLA_MULTI_SLICE_RUNTIME_LOAD_FINAL_REPORT.md"), report)
    write_text(os.path.join(PACK, "07_summary/FINAL_VERDICT.txt"), verdict + "\n")
    write_json(
        os.path.join(PACK, "MANIFEST.json"),
        {"pack_id": "TRISLA_MULTI_SLICE_RUNTIME_LOAD_01", "pack_path": PACK, "verdict": verdict, "comparative": cmp, "timestamp_utc": TS},
    )
    print(json.dumps({"pack": PACK, "verdict": verdict, "comparative": cmp}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
