#!/usr/bin/env python3
"""O4C runtime validation — D1/D2/D6 via portal-backend SLA submit + RAN binding fields."""
import json
import subprocess
import sys
import time
from datetime import datetime, timezone

RAN_KEYS = (
    "binding_phase",
    "supi",
    "gnb_id",
    "ran_ue_ngap_id",
    "amf_ue_ngap_id",
    "serving_snssai",
    "fresh_ue_ip",
    "session_id",
    "selected_upf",
    "upf_gtpu_addr",
    "dnn",
    "correlation_status",
    "access_correlated",
    "freshness_source",
)

CASES = [
    (
        "D1",
        "URLLC",
        "urllc-template-001",
        {"type": "URLLC", "latency": "1ms", "reliability": 0.99999, "throughput": "100Mbps", "service_name": "O4C-D1", "intent_text": "O4C URLLC"},
    ),
    (
        "D2",
        "mMTC",
        "mmtc-template-001",
        {"type": "mMTC", "device_density": 1000000, "coverage": "Urban", "service_name": "O4C-D2", "intent_text": "O4C mMTC"},
    ),
    (
        "D6",
        "eMBB",
        "embb-template-001",
        {"type": "eMBB", "throughput": "1Gbps", "service_name": "O4C-D6", "intent_text": "O4C eMBB"},
    ),
)


def kubectl(*args, text=True):
    return subprocess.check_output(["kubectl", "-n", "trisla", *args], text=text)


def portal_submit(template_id, tenant_id, form_values):
    pb = kubectl("get", "pods", "-l", "app=trisla-portal-backend", "-o", "jsonpath={.items[0].metadata.name}").strip()
    body = {"template_id": template_id, "tenant_id": tenant_id, "form_values": form_values}
    code = f"""
import json, urllib.request
body = {json.dumps(body)}
req = urllib.request.Request("http://127.0.0.1:8888/api/v1/sla/submit", data=json.dumps(body).encode(), headers={{"Content-Type":"application/json"}}, method="POST")
print(urllib.request.urlopen(req, timeout=180).read().decode())
"""
    out = kubectl("exec", pb, "--", "python", "-c", code)
    return json.loads(out.strip().split("\n")[-1])


def get_nsi(nest_id):
    raw = kubectl("get", "networksliceinstances.trisla.io", nest_id, "-o", "json")
    return json.loads(raw)


def curl_binding_status(nsi_id):
    pod = f"o4c-st-{int(time.time())}"
    out = subprocess.check_output(
        [
            "kubectl",
            "-n",
            "trisla",
            "run",
            pod,
            "--rm",
            "-i",
            "--restart=Never",
            "--image=curlimages/curl:8.5.0",
            "--",
            "curl",
            "-s",
            f"http://trisla-nasp-adapter:8085/api/v1/slice-service-binding/binding/status/{nsi_id}",
        ],
        stderr=subprocess.DEVNULL,
        text=True,
    )
    return json.loads(out.split("pod")[0].strip())


def parse_ann_json(ann, key):
    raw = ann.get(key)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw[:200]}


def main():
    results = []
    for case, profile, template, fv in CASES:
        tenant = f"o4c-{case.lower()}-{int(time.time())}"
        print(f"\n=== {case} {profile} tenant={tenant} ===", flush=True)
        submit = portal_submit(template, tenant, fv)
        nest = submit.get("nest_id")
        row = {
            "case": case,
            "profile": profile,
            "decision": submit.get("decision"),
            "bc_status": submit.get("bc_status"),
            "sla_agent": submit.get("sla_agent_status"),
            "nest_id": nest,
        }
        print("submit:", json.dumps({k: row[k] for k in row}, indent=2), flush=True)
        if not nest:
            results.append(row)
            continue
        time.sleep(12)
        try:
            nsi = get_nsi(nest)
        except subprocess.CalledProcessError:
            row["error"] = "NSI not found"
            results.append(row)
            continue

        ann = (nsi.get("metadata") or {}).get("annotations") or {}
        labels = (nsi.get("metadata") or {}).get("labels") or {}
        ssb = parse_ann_json(ann, "trisla.io/slice-service-binding") or {}
        ran = parse_ann_json(ann, "trisla.io/ran-binding") or {}
        pdu = parse_ann_json(ann, "trisla.io/pdu-session-summary") or {}

        try:
            status = curl_binding_status(nest)
        except Exception as exc:
            status = {"error": str(exc)}

        row.update(
            {
                "binding_phase": ssb.get("binding_phase") or labels.get("trisla.io/binding-phase"),
                "ran_integrated": labels.get("trisla.io/ran-integrated"),
                "ran_binding_status": ran.get("binding_status"),
                "gnb_id": ran.get("gnb_id") or pdu.get("gnb_id"),
                "ran_ue_ngap_id": ran.get("ran_ue_ngap_id") or pdu.get("ran_ue_ngap_id"),
                "amf_ue_ngap_id": ran.get("amf_ue_ngap_id") or pdu.get("amf_ue_ngap_id"),
                "supi": ran.get("supi") or pdu.get("supi"),
                "serving_snssai": ran.get("serving_snssai") or pdu.get("serving_snssai"),
                "fresh_ue_ip": pdu.get("fresh_ue_ip"),
                "session_id": ran.get("session_id") or pdu.get("session_id"),
                "selected_upf": pdu.get("selected_upf"),
                "upf_gtpu_addr": pdu.get("upf_gtpu_addr"),
                "dnn": ran.get("dnn") or pdu.get("dnn"),
                "correlation_status": ran.get("correlation_status") or pdu.get("correlation_status"),
                "access_correlated": pdu.get("access_correlated"),
                "freshness_source": ran.get("freshness_source") or pdu.get("freshness_source"),
                "api_status": status,
            }
        )
        print("binding:", json.dumps({k: row.get(k) for k in RAN_KEYS if row.get(k) is not None}, indent=2), flush=True)
        results.append(row)

    out_path = f"/home/porvir5g/gtp5g/trisla/runtime/o4c_runtime_validation.json"
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": "O4C",
        "results": results,
    }
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    print(f"\nWrote {out_path}", flush=True)

    ok = all(
        r.get("decision") == "ACCEPT"
        and r.get("bc_status") in ("COMMITTED", "OK", None)
        and r.get("binding_phase") in ("ACCESS_CORRELATED", "RAN_OBSERVED", "USER_PLANE_CORRELATED")
        for r in results
        if r.get("nest_id")
    )
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
