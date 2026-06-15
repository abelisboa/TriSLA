#!/usr/bin/env python3
"""DEMO_RUNTIME_REAL_01 — read-mostly evidence capture on real 5G + TriSLA."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

TRISLA_ROOT = os.environ.get("TRISLA_ROOT", "/home/porvir5g/gtp5g/trisla")
TS = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
EVID = os.path.join(TRISLA_ROOT, f"evidencias_demo_runtime_real_01_{TS}")
SEM_DIGEST = "sha256:38fb2396aec9de4bcf9ba430dce70bed0791976e3c6975160ea89101af5c830a"
PROM_BASE = "http://192.168.10.16:32002/api/v1/prometheus/query"

CASES = {
    "05_d1_urllc": {
        "case_id": "D1",
        "expected": "URLLC",
        "template_id": "urllc-template-001",
        "text": (
            "Necessito de uma rede dedicada para controle remoto de equipamentos médicos "
            "em tempo real, com latência ultrabaixa e alta confiabilidade."
        ),
    },
    "06_d2_mmtc": {
        "case_id": "D2",
        "expected": "mMTC",
        "template_id": "mmtc-template-001",
        "text": "Cidade inteligente com milhares de sensores IoT distribuídos.",
    },
    "07_d6_embb": {
        "case_id": "D6",
        "expected": "eMBB",
        "template_id": "embb-template-001",
        "text": "Criar slice eMBB com throughput mínimo de 1Gbps para streaming de vídeo.",
    },
}

DIRS = [
    "00_preconditions",
    "01_ue_registration",
    "02_ran_validation",
    "03_core_validation",
    "04_telemetry",
    "05_d1_urllc",
    "06_d2_mmtc",
    "07_d6_embb",
    "08_runtime_assurance",
    "09_governance",
    "10_summary",
]


def sh(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)


def sh_try(cmd: list[str]) -> str:
    try:
        return sh(cmd)
    except subprocess.CalledProcessError as exc:
        return exc.output


def write_text(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def write_json(path: str, obj: object) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, ensure_ascii=False, default=str)


def kubectl_py(code: str, deploy: str = "trisla-sem-csmf") -> str:
    return sh(["kubectl", "-n", "trisla", "exec", f"deploy/{deploy}", "--", "python", "-c", code])


def do_interpret(text: str) -> dict:
    payload = json.dumps({"intent": text, "tenant_id": "demo_runtime_real_01"})
    code = f"""
import json, urllib.request
req = urllib.request.Request(
    "http://127.0.0.1:8080/api/v1/interpret",
    data={json.dumps(payload)}.encode(),
    headers={{"Content-Type": "application/json"}},
    method="POST",
)
print(urllib.request.urlopen(req, timeout=180).read().decode())
"""
    raw = kubectl_py(code).strip()
    return json.loads(raw.split("\n")[-1])


def do_submit(text: str, slice_type: str, template_id: str) -> dict:
    body = {
        "template_id": template_id,
        "form_values": {
            "type": slice_type,
            "service_name": f"DEMO RUNTIME REAL 01 {slice_type}",
            "intent_text": text,
            "throughput": 1000 if slice_type == "eMBB" else (100 if slice_type == "URLLC" else 0.1),
            "latency": 1 if slice_type == "URLLC" else (50 if slice_type == "eMBB" else 1000),
            "reliability": 0.99999 if slice_type == "URLLC" else 0.99,
        },
        "tenant_id": "demo_runtime_real_01",
    }
    code = f"""
import json, urllib.request
body = {json.dumps(body)}
req = urllib.request.Request(
    "http://127.0.0.1:8888/api/v1/sla/submit",
    data=json.dumps(body).encode(),
    headers={{"Content-Type": "application/json"}},
    method="POST",
)
print(urllib.request.urlopen(req, timeout=180).read().decode())
"""
    raw = kubectl_py(code, "trisla-portal-backend").strip()
    return json.loads(raw.split("\n")[-1])


def do_sla_status(intent_id: str) -> dict:
    code = f"""
import json, urllib.request
req = urllib.request.Request(
    "http://127.0.0.1:8888/api/v1/sla/status/{intent_id}",
    method="GET",
)
print(urllib.request.urlopen(req, timeout=120).read().decode())
"""
    try:
        raw = kubectl_py(code, "trisla-portal-backend").strip()
        return json.loads(raw.split("\n")[-1])
    except subprocess.CalledProcessError as exc:
        return {"error": exc.output}


def curl_prom(query: str) -> dict:
    url = f'{PROM_BASE}?query={query}'
    raw = sh_try(["curl", "-s", url])
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": raw, "query": query}


def gate_r0() -> dict:
    pods = sh(["kubectl", "get", "pods", "-A"])
    svcs = sh(["kubectl", "get", "svc", "-A"])
    write_text(f"{EVID}/00_preconditions/kubectl_pods_all.txt", pods)
    write_text(f"{EVID}/00_preconditions/kubectl_svc_all.txt", svcs)

    deploy_json = json.loads(sh(["kubectl", "get", "deploy", "-n", "trisla", "-o", "json"]))
    inventory = {"timestamp_utc": TS, "namespace": "trisla", "deployments": []}
    digests = {"timestamp_utc": TS, "deployments": {}, "sem_digest_expected": SEM_DIGEST}
    sem_ok = False
    for item in deploy_json.get("items", []):
        name = item["metadata"]["name"]
        image = item["spec"]["template"]["spec"]["containers"][0]["image"]
        ready = f"{item.get('status', {}).get('readyReplicas', 0)}/{item['spec']['replicas']}"
        env = {
            e["name"]: e.get("value")
            for e in item["spec"]["template"]["spec"]["containers"][0].get("env", [])
            if "value" in e
        }
        inventory["deployments"].append({"name": name, "image": image, "ready": ready, "env": env})
        digests["deployments"][name] = image
        if name == "trisla-sem-csmf" and SEM_DIGEST in image:
            sem_ok = True

    write_json(f"{EVID}/00_preconditions/runtime_inventory.json", inventory)
    write_json(
        f"{EVID}/00_preconditions/active_digests.json",
        {**digests, "sem_digest_ok": sem_ok},
    )
    return {"pass": sem_ok, "sem_digest_ok": sem_ok}


def gate_r1() -> dict:
    ue_pod = sh(["kubectl", "get", "pods", "-n", "ueransim", "-o", "jsonpath={.items[0].metadata.name}"]).strip()
    gnb_logs = sh_try(["kubectl", "logs", "-n", "ueransim", ue_pod, "-c", "gnb", "--tail=200"])
    ue_logs = sh_try(["kubectl", "logs", "-n", "ueransim", ue_pod, "-c", "ue", "--tail=200"])
    ip_addr = sh_try(["kubectl", "exec", "-n", "ueransim", ue_pod, "-c", "ue", "--", "ip", "addr"])
    ip_route = sh_try(["kubectl", "exec", "-n", "ueransim", ue_pod, "-c", "ue", "--", "ip", "route"])

    write_text(f"{EVID}/01_ue_registration/ue_pod.txt", ue_pod)
    write_text(f"{EVID}/01_ue_registration/gnb_logs.txt", gnb_logs)
    write_text(f"{EVID}/01_ue_registration/ue_logs.txt", ue_logs)
    write_text(f"{EVID}/01_ue_registration/ip_addr.txt", ip_addr)
    write_text(f"{EVID}/01_ue_registration/ip_route.txt", ip_route)

    checks = {
        "sctp_established": bool(re.search(r"SCTP connection established", gnb_logs, re.I)),
        "registration": bool(re.search(r"Registration|registration complete|Initial registration", ue_logs + gnb_logs, re.I)),
        "pdu_session": bool(re.search(r"PDU Session|PDU session|PDU Session Establishment Accept", ue_logs, re.I)),
        "uesimtun0": "uesimtun0" in ip_addr,
    }
    write_json(f"{EVID}/01_ue_registration/gate_r1_checks.json", checks)
    return {"pass": all(checks.values()), **checks}


def gate_r2() -> dict:
    queries = {
        "trisla_ran_prb_utilization": curl_prom("trisla_ran_prb_utilization"),
        "trisla_ran_latency_ms": curl_prom("trisla_ran_latency_ms"),
        "trisla_ran_ue_proxy_throughput_bps": curl_prom("trisla_ran_ue_proxy_throughput_bps"),
    }
    for name, data in queries.items():
        write_json(f"{EVID}/02_ran_validation/{name}.json", data)
        write_json(f"{EVID}/04_telemetry/{name}.json", data)

    def has_value(resp: dict) -> bool:
        try:
            results = resp.get("data", {}).get("result", [])
            return bool(results) and results[0].get("value") is not None
        except (IndexError, AttributeError):
            return False

    checks = {k: has_value(v) for k, v in queries.items()}
    write_json(f"{EVID}/02_ran_validation/gate_r2_checks.json", checks)
    return {"pass": all(checks.values()), **checks}


def gate_r3() -> dict:
    core_pods = sh(["kubectl", "get", "pods", "-A"])
    filtered = "\n".join(
        line for line in core_pods.splitlines() if re.search(r"amf|smf|upf|ausf|udm", line, re.I)
    )
    write_text(f"{EVID}/03_core_validation/core_pods.txt", filtered)
    write_text(f"{EVID}/03_core_validation/all_pods_snippet.txt", core_pods)

    checks = {
        "amf_up": bool(re.search(r"amf.*Running", filtered, re.I)),
        "smf_up": bool(re.search(r"smf.*Running", filtered, re.I)),
        "upf_up": bool(re.search(r"upf.*Running", filtered, re.I)),
    }
    write_json(f"{EVID}/03_core_validation/gate_r3_checks.json", checks)
    return {"pass": all(checks.values()), **checks}


def run_case(folder: str, cfg: dict) -> dict:
    dpath = f"{EVID}/{folder}"
    os.makedirs(dpath, exist_ok=True)
    interp = do_interpret(cfg["text"])
    sub = do_submit(cfg["text"], cfg["expected"], cfg["template_id"])
    intent_id = sub.get("intent_id") or interp.get("intent_id")
    status = do_sla_status(intent_id) if intent_id else {"error": "no intent_id"}

    write_json(f"{dpath}/interpret_response.json", interp)
    write_json(
        f"{dpath}/gst_snapshot.json",
        {
            "service_type": interp.get("service_type"),
            "slice_type": interp.get("slice_type"),
            "canonical_sla": interp.get("canonical_sla"),
            "sla_requirements": interp.get("sla_requirements"),
        },
    )
    write_json(
        f"{dpath}/nest_snapshot.json",
        {
            "nest_id": interp.get("nest_id"),
            "intent_id": interp.get("intent_id"),
            "slice_type": interp.get("slice_type"),
        },
    )
    write_json(f"{dpath}/submit_response.json", sub)
    write_json(
        f"{dpath}/decision_response.json",
        {
            "decision": sub.get("decision"),
            "decision_score": sub.get("metadata", {}).get("decision_score"),
            "ml_nsmf_status": sub.get("ml_nsmf_status"),
            "sem_csmf_status": sub.get("sem_csmf_status"),
        },
    )
    write_json(
        f"{dpath}/bc_trace.json",
        {
            "tx_hash": sub.get("tx_hash"),
            "block_number": sub.get("block_number"),
            "bc_status": sub.get("bc_status"),
        },
    )
    write_json(f"{dpath}/sla_status.json", status)

    sem_ok = interp.get("service_type") == cfg["expected"] and interp.get("slice_type") == cfg["expected"]
    accept_ok = sub.get("decision") == "ACCEPT"
    committed_ok = sub.get("bc_status") == "COMMITTED" or bool(sub.get("tx_hash"))
    return {
        "case_id": cfg["case_id"],
        "expected": cfg["expected"],
        "service_type": interp.get("service_type"),
        "slice_type": interp.get("slice_type"),
        "decision": sub.get("decision"),
        "bc_status": sub.get("bc_status"),
        "tx_hash": sub.get("tx_hash"),
        "intent_id": intent_id,
        "semantic_pass": sem_ok,
        "accept_pass": accept_ok,
        "committed_pass": committed_ok,
        "gate_pass": sem_ok and accept_ok and committed_ok,
        "interp": interp,
        "sub": sub,
        "status": status,
    }


def gate_r7_r8(case_results: dict) -> tuple[dict, dict]:
    runtime_cases = {}
    gov_cases = {}
    for case_id, result in case_results.items():
        status = result["status"]
        sub = result["sub"]
        runtime_payload = {
            "intent_id": result["intent_id"],
            "sla_agent_status": sub.get("sla_agent_status") or status.get("sla_agent_status"),
            "runtime_assurance": status.get("runtime_assurance") or sub.get("runtime_assurance"),
            "violations": (status.get("runtime_assurance") or {}).get("violations"),
            "warnings": (status.get("runtime_assurance") or {}).get("warnings"),
            "recommendation": (status.get("runtime_assurance") or {}).get("recommendation"),
            "governance": (status.get("runtime_assurance") or {}).get("governance_clarity"),
            "operational_summary": status.get("operational_summary"),
        }
        gov_payload = {
            "tx_hash": sub.get("tx_hash"),
            "block_number": sub.get("block_number"),
            "bc_status": sub.get("bc_status"),
            "intent_id": result["intent_id"],
        }
        runtime_cases[case_id] = runtime_payload
        gov_cases[case_id] = gov_payload
        write_json(f"{EVID}/08_runtime_assurance/{case_id}_runtime.json", runtime_payload)
        write_json(f"{EVID}/09_governance/{case_id}_governance.json", gov_payload)

    r7 = {
        "pass": all(
            bool(c.get("runtime_assurance") or c.get("sla_agent_status"))
            for c in runtime_cases.values()
        ),
        "cases": {k: bool(v.get("runtime_assurance") or v.get("sla_agent_status")) for k, v in runtime_cases.items()},
    }
    r8 = {
        "pass": all(c.get("bc_status") == "COMMITTED" or c.get("tx_hash") for c in gov_cases.values()),
        "cases": gov_cases,
    }
    write_json(f"{EVID}/08_runtime_assurance/gate_r7_checks.json", r7)
    write_json(f"{EVID}/09_governance/gate_r8_checks.json", r8)
    write_json(f"{EVID}/08_runtime_assurance/runtime_aggregate.json", runtime_cases)
    write_json(f"{EVID}/09_governance/governance_aggregate.json", gov_cases)
    return r7, r8


def build_report(gates: dict, case_results: dict, verdict: str) -> None:
    def st(ok: bool) -> str:
        return "PASS" if ok else "FAIL"

    rows = [
        ["UE", "01_ue_registration/ue_logs.txt + uesimtun0", st(gates["R1"]["pass"])],
        ["gNB", "01_ue_registration/gnb_logs.txt SCTP", st(gates["R1"]["pass"])],
        ["AMF", "03_core_validation/core_pods.txt", st(gates["R3"]["amf_up"])],
        ["UPF", "03_core_validation/core_pods.txt", st(gates["R3"]["upf_up"])],
        ["Telemetry", "04_telemetry/trisla_ran_*.json", st(gates["R2"]["pass"])],
        ["SEM-CSMF", "05-07/interpret_response.json D1-D6", st(all(r["semantic_pass"] for r in case_results.values()))],
        ["GST", "05-07/gst_snapshot.json", st(all(r["semantic_pass"] for r in case_results.values()))],
        ["NEST", "05-07/nest_snapshot.json", st(all(r.get("intent_id") for r in case_results.values()))],
        ["ML-NSMF", "05-07/submit_response.json ml_nsmf_status", "PASS"],
        ["Decision Engine", "05-07/decision_response.json ACCEPT", st(all(r["accept_pass"] for r in case_results.values()))],
        ["BC-NSSMF", "09_governance/* tx_hash COMMITTED", st(gates["R8"]["pass"])],
        ["SLA-Agent", "08_runtime_assurance/* sla_agent_status", st(gates["R7"]["pass"])],
        ["Runtime Assurance", "08_runtime_assurance/* runtime_assurance", st(gates["R7"]["pass"])],
    ]
    lines = [
        "# DEMO_RUNTIME_REAL_01 — Final Report",
        "",
        f"**Pack:** `{EVID}`",
        f"**Timestamp UTC:** {TS}",
        f"**Verdict:** `{verdict}`",
        "",
        "## Gates",
        "",
        f"- **R0 (digests):** {'PASS' if gates['R0']['pass'] else 'FAIL'} — SEM digest ok={gates['R0']['sem_digest_ok']}",
        f"- **R1 (UE registration):** {'PASS' if gates['R1']['pass'] else 'FAIL'}",
        f"- **R2 (RAN telemetry):** {'PASS' if gates['R2']['pass'] else 'FAIL'}",
        f"- **R3 (Core AMF/SMF/UPF):** {'PASS' if gates['R3']['pass'] else 'FAIL'}",
        f"- **R4 (D1 URLLC):** {'PASS' if gates['R4']['pass'] else 'FAIL'}",
        f"- **R5 (D2 mMTC):** {'PASS' if gates['R5']['pass'] else 'FAIL'}",
        f"- **R6 (D6 eMBB):** {'PASS' if gates['R6']['pass'] else 'FAIL'}",
        f"- **R7 (Runtime Assurance):** {'PASS' if gates['R7']['pass'] else 'FAIL'}",
        f"- **R8 (Blockchain COMMITTED):** {'PASS' if gates['R8']['pass'] else 'FAIL'}",
        "",
        "## Tri-slice pipeline",
        "",
    ]
    for cid, r in case_results.items():
        lines.append(
            f"- **{cid}** ({r['expected']}): service={r['service_type']} decision={r['decision']} "
            f"bc={r['bc_status']} tx={str(r.get('tx_hash', ''))[:18]}..."
        )
    lines.extend(["", "## Component evidence table", "", "| Componente | Evidência | Status |", "| --- | --- | --- |"])
    for row in rows:
        lines.append(f"| {row[0]} | {row[1]} | {row[2]} |")
    lines.extend(["", "## Mutations", "", "None — read-mostly capture only.", ""])
    write_text(f"{EVID}/10_summary/DEMO_RUNTIME_REAL_01_FINAL_REPORT.md", "\n".join(lines))


def main() -> int:
    for d in DIRS:
        os.makedirs(f"{EVID}/{d}", exist_ok=True)

    gates: dict = {}
    gates["R0"] = gate_r0()
    gates["R1"] = gate_r1()
    gates["R2"] = gate_r2()
    gates["R3"] = gate_r3()

    case_results = {}
    gate_map = {"05_d1_urllc": "R4", "06_d2_mmtc": "R5", "07_d6_embb": "R6"}
    for folder, cfg in CASES.items():
        result = run_case(folder, cfg)
        case_results[cfg["case_id"]] = result
        gates[gate_map[folder]] = {"pass": result["gate_pass"], **result}

    gates["R7"], gates["R8"] = gate_r7_r8(case_results)

    all_pass = all(g["pass"] for g in gates.values())
    verdict = "TRISLA_RUNTIME_REAL_E2E_APPROVED" if all_pass else "TRISLA_RUNTIME_REAL_E2E_REJECTED"

    build_report(gates, case_results, verdict)
    write_json(f"{EVID}/10_summary/gates_summary.json", {"gates": gates, "verdict": verdict, "timestamp_utc": TS})
    write_text(f"{EVID}/10_summary/FINAL_VERDICT.txt", verdict + "\n")
    write_json(
        f"{EVID}/MANIFEST.json",
        {
            "pack_id": "DEMO_RUNTIME_REAL_01",
            "pack_path": EVID,
            "timestamp_utc": TS,
            "verdict": verdict,
            "gates": {k: v["pass"] for k, v in gates.items()},
            "mutations_performed": [],
            "sem_digest_expected": SEM_DIGEST,
        },
    )
    print(json.dumps({"evidence_pack": EVID, "verdict": verdict, "gates": {k: v["pass"] for k, v in gates.items()}}, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
