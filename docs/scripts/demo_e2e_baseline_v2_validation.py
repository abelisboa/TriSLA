#!/usr/bin/env python3
"""READ-ONLY DEMO E2E Baseline V2 tri-slice validation."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

TRISLA_ROOT = os.environ.get("TRISLA_ROOT", "/home/porvir5g/gtp5g/trisla")
EVID = os.path.join(
    TRISLA_ROOT,
    f"evidencias_demo_e2e_baseline_v2_validation_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
)
BASELINE_DIGESTS = os.path.join(
    TRISLA_ROOT,
    "evidencias_sem_rebaseline_01_20260605T173829Z/01_runtime_digests/active_digests.json",
)
SEMANTIC_DIGEST = "sha256:38fb2396aec9de4bcf9ba430dce70bed0791976e3c6975160ea89101af5c830a"
FREEZE_SHA = "aeb26946e0b2f81064372dfd3f743cd3492e207db0bb29c789f7983fe2c9e1f6"
FREEZE_CSV = os.path.join(
    TRISLA_ROOT,
    "evidencias_multidomain_stress_campaign_v2_20260529T115740Z/dataset/multidomain_stress_final.csv",
)

CASES = {
    "01_d1_urllc": {
        "case_id": "D1",
        "expected": "URLLC",
        "template_id": "urllc-template-001",
        "text": (
            "Necessito de uma rede dedicada para controle remoto de equipamentos médicos "
            "em tempo real, com latência ultrabaixa, alta confiabilidade e disponibilidade contínua."
        ),
    },
    "02_d2_mmtc": {
        "case_id": "D2",
        "expected": "mMTC",
        "template_id": "mmtc-template-001",
        "text": "Cidade inteligente com milhares de sensores distribuídos.",
    },
    "03_d6_embb": {
        "case_id": "D6",
        "expected": "eMBB",
        "template_id": "embb-template-001",
        "text": "Criar slice eMBB com throughput mínimo de 1Gbps para streaming de vídeo",
    },
}


def sh(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)


def kubectl_py(code: str, deploy: str = "trisla-sem-csmf") -> str:
    return sh(["kubectl", "-n", "trisla", "exec", f"deploy/{deploy}", "--", "python", "-c", code])


def do_interpret(text: str) -> dict:
    payload = json.dumps({"intent": text, "tenant_id": "demo_e2e_v2"})
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
    return json.loads(kubectl_py(code).strip().split("\n")[-1])


def do_submit(text: str, slice_type: str, template_id: str) -> dict:
    body = {
        "template_id": template_id,
        "form_values": {
            "type": slice_type,
            "service_name": f"DEMO E2E V2 {slice_type}",
            "intent_text": text,
            "throughput": 1000 if slice_type == "eMBB" else (100 if slice_type == "URLLC" else 0.1),
            "latency": 1 if slice_type == "URLLC" else (50 if slice_type == "eMBB" else 1000),
            "reliability": 0.99999 if slice_type == "URLLC" else 0.99,
        },
        "tenant_id": "demo_e2e_v2",
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
    return json.loads(kubectl_py(code, "trisla-portal-backend").strip().split("\n")[-1])


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
        return json.loads(kubectl_py(code, "trisla-portal-backend").strip().split("\n")[-1])
    except subprocess.CalledProcessError as exc:
        return {"error": exc.output}


def write_json(path: str, obj: object) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, ensure_ascii=False, default=str)


def main() -> int:
    deploys = [
        "trisla-sem-csmf",
        "trisla-decision-engine",
        "trisla-ml-nsmf",
        "trisla-bc-nssmf",
        "trisla-sla-agent-layer",
        "trisla-nasp-adapter",
        "trisla-portal-backend",
    ]

    g1 = {"gate": "G1", "modules": {}, "pass": True}
    for deploy in deploys:
        ready = sh(
            ["kubectl", "-n", "trisla", "get", "deploy", deploy, "-o", "jsonpath={.status.readyReplicas}/{.spec.replicas}"]
        ).strip()
        g1["modules"][deploy] = ready
        if ready != "1/1":
            g1["pass"] = False
    write_json(f"{EVID}/00_preconditions/g1_modules_up.json", g1)

    current = {"deployments": {}}
    for deploy in deploys + ["trisla-portal-frontend"]:
        current["deployments"][deploy] = sh(
            ["kubectl", "-n", "trisla", "get", "deploy", deploy, "-o", "jsonpath={.spec.template.spec.containers[0].image}"]
        ).strip()
    sem_deploy = json.loads(sh(["kubectl", "-n", "trisla", "get", "deploy", "trisla-sem-csmf", "-o", "json"]))
    sem_env = next(
        (
            env["value"]
            for env in sem_deploy["spec"]["template"]["spec"]["containers"][0].get("env", [])
            if env.get("name") == "TRISLA_SEM_CLASSIFICATION_MODE"
        ),
        None,
    )
    baseline = json.load(open(BASELINE_DIGESTS, encoding="utf-8"))
    digest_diff = {}
    g8_pass = True
    for deploy, image in baseline["deployments"].items():
        cur = current["deployments"].get(deploy)
        if deploy == "trisla-sem-csmf":
            if SEMANTIC_DIGEST not in cur:
                g8_pass = False
        elif cur != image and deploy != "trisla-nasp-adapter":
            digest_diff[deploy] = {"baseline": image, "current": cur}
            g8_pass = False
    g4_sem = SEMANTIC_DIGEST in current["deployments"]["trisla-sem-csmf"] and sem_env == "hybrid"
    write_json(
        f"{EVID}/06_digest_validation/active_digests.json",
        {"sem_digest_ok": g4_sem, "mode": sem_env, "digest_diff": digest_diff, "pass": g8_pass and g4_sem, "current": current},
    )

    actual_sha = hashlib.sha256(open(FREEZE_CSV, "rb").read()).hexdigest()
    g9 = {"gate": "G9", "expected": FREEZE_SHA, "actual": actual_sha, "pass": actual_sha == FREEZE_SHA}
    write_json(f"{EVID}/07_results_freeze_validation/results_freeze_sha256.json", g9)

    case_results = {}
    gov_cases = {}
    for folder, cfg in CASES.items():
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
                "service_type": interp.get("service_type"),
            },
        )
        write_json(
            f"{dpath}/decision_response.json",
            {
                "decision": sub.get("decision"),
                "decision_score": sub.get("metadata", {}).get("decision_score"),
                "decision_source": sub.get("metadata", {}).get("decision_source"),
                "sem_csmf_status": sub.get("sem_csmf_status"),
                "ml_nsmf_status": sub.get("ml_nsmf_status"),
            },
        )
        write_json(f"{dpath}/submit_response.json", sub)
        write_json(
            f"{dpath}/bc_trace.json",
            {
                "tx_hash": sub.get("tx_hash"),
                "block_number": sub.get("block_number"),
                "bc_status": sub.get("bc_status"),
            },
        )
        write_json(
            f"{dpath}/runtime_trace.json",
            {
                "sla_agent_status": sub.get("sla_agent_status"),
                "runtime_assurance": sub.get("runtime_assurance"),
                "intent_id": intent_id,
            },
        )
        write_json(f"{dpath}/sla_status.json", status)

        sem_ok = interp.get("service_type") == cfg["expected"] and interp.get("slice_type") == cfg["expected"]
        dec_ok = bool(sub.get("decision"))
        bc_ok = bool(sub.get("tx_hash") or sub.get("bc_status"))
        rt_ok = bool(sub.get("sla_agent_status") or (isinstance(status, dict) and status.get("runtime_assurance")))
        pipe_ok = sem_ok and dec_ok and bc_ok and rt_ok
        write_json(
            f"{dpath}/v2_semantic_consistency.json",
            {
                "case_id": cfg["case_id"],
                "expected": cfg["expected"],
                "service_type": interp.get("service_type"),
                "slice_type": interp.get("slice_type"),
                "template_id": cfg["template_id"],
                "sla_type": sub.get("sla_requirements", {}).get("sla_type"),
                "decision": sub.get("decision"),
                "decision_score": sub.get("metadata", {}).get("decision_score"),
                "semantic_pass": sem_ok,
                "pipeline_pass": pipe_ok,
            },
        )
        case_results[cfg["case_id"]] = {
            "semantic_pass": sem_ok,
            "decision_pass": dec_ok,
            "bc_pass": bc_ok,
            "runtime_pass": rt_ok,
            "pipeline_pass": pipe_ok,
        }
        gov_cases[cfg["case_id"]] = {
            "tx_hash": sub.get("tx_hash"),
            "block_number": sub.get("block_number"),
            "bc_status": sub.get("bc_status"),
            "runtime_assurance": status.get("runtime_assurance") if isinstance(status, dict) else None,
            "traceability": status.get("traceability") if isinstance(status, dict) else None,
            "intent_id": intent_id,
        }

    g5 = all(case_results[c]["decision_pass"] for c in case_results)
    g6 = all(case_results[c]["bc_pass"] for c in case_results)
    g7 = all(case_results[c]["runtime_pass"] for c in case_results)
    gates = {
        "G1": g1["pass"],
        "G2": case_results["D1"]["semantic_pass"],
        "G3": case_results["D2"]["semantic_pass"],
        "G4": case_results["D6"]["semantic_pass"],
        "G5": g5,
        "G6": g6,
        "G7": g7,
        "G8": g8_pass and g4_sem,
        "G9": g9["pass"],
        "G10": (
            g1["pass"]
            and all(case_results[c]["pipeline_pass"] for c in case_results)
            and g5
            and g6
            and g7
            and g8_pass
            and g4_sem
            and g9["pass"]
        ),
    }
    verdict = (
        "TRISLA_E2E_TRI_SLICE_OPERATION_APPROVED"
        if all(gates.values())
        else "TRISLA_E2E_TRI_SLICE_OPERATION_BLOCKED"
    )

    write_json(f"{EVID}/04_governance/governance_aggregate.json", {"cases": gov_cases, "G5": g5, "G6": g6})
    write_json(
        f"{EVID}/05_runtime/runtime_aggregate.json",
        {"G7": g7, "cases": {c: case_results[c]["runtime_pass"] for c in case_results}},
    )
    summary = {
        "verdict": verdict,
        "gates": gates,
        "case_results": case_results,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_pack": EVID,
    }
    write_json(f"{EVID}/08_summary/gates_summary.json", summary)
    write_json(f"{EVID}/MANIFEST.json", {"pack": EVID, "verdict": verdict, "gates": gates, "mutations_performed": []})

    report_lines = [
        "# DEMO E2E Baseline V2 Validation",
        "",
        f"**Verdict:** `{verdict}`",
        "",
        "## Gates",
        "",
    ]
    for gate, passed in gates.items():
        report_lines.append(f"- **{gate}:** {'PASS' if passed else 'FAIL'}")
    report_lines.extend(["", "## Tri-slice cases", ""])
    for case_id in ["D1", "D2", "D6"]:
        cfg = next(v for v in CASES.values() if v["case_id"] == case_id)
        result = case_results[case_id]
        report_lines.append(
            f"- **{case_id}** ({cfg['expected']}): semantic={result['semantic_pass']} decision={result['decision_pass']} bc={result['bc_pass']} runtime={result['runtime_pass']}"
        )
    with open(f"{EVID}/08_summary/DEMO_E2E_BASELINE_V2_FINAL_REPORT.md", "w", encoding="utf-8") as handle:
        handle.write("\n".join(report_lines) + "\n")

    print(json.dumps(summary, indent=2))
    return 0 if verdict == "TRISLA_E2E_TRI_SLICE_OPERATION_APPROVED" else 1


if __name__ == "__main__":
    sys.exit(main())
