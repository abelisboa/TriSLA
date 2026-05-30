#!/usr/bin/env python3
"""Sprint 5M1 E2E — governance_event.nest_id vs runtime nest_id."""
from __future__ import annotations

import json
import sys
import time
import uuid
from pathlib import Path

import requests

BE = "http://192.168.10.15:32002/api/v1/sla"
OUT = Path(__file__).resolve().parent

INTENTS = [
    ("urllc", "cirurgia remota", "urllc-template-001"),
    ("embb", "vídeo 4K", "embb-template-001"),
    ("mmtc", "sensores IoT", "mmtc-template-001"),
    ("smartcity", "cidade inteligente", "embb-template-001"),
]


def build_form_values(interpret: dict) -> dict:
    req = dict(interpret.get("sla_requirements") or {})
    st = interpret.get("service_type") or interpret.get("slice_type")
    if st:
        req.setdefault("type", st)
        req.setdefault("slice_type", st)
        req.setdefault("sla_type", st)
    req.setdefault("template_id", interpret.get("template_id"))
    return req


def main() -> int:
    results = {}
    failures = []

    for key, intent_text, template_id in INTENTS:
        tenant = f"trisla-5m1-{uuid.uuid4().hex[:8]}"
        print(f"[E2E] {key}: interpret …", flush=True)
        ir = requests.post(
            f"{BE}/interpret",
            json={"intent_text": intent_text, "tenant_id": tenant},
            timeout=120,
        )
        ir.raise_for_status()
        interpret = ir.json()
        (OUT / f"interpret_{key}.json").write_text(
            json.dumps(interpret, indent=2, ensure_ascii=False)
        )

        form_values = build_form_values(interpret)
        form_values["template_id"] = template_id
        submit_body = {
            "template_id": template_id,
            "form_values": form_values,
            "tenant_id": tenant,
        }
        print(f"[E2E] {key}: submit …", flush=True)
        sr = requests.post(f"{BE}/submit", json=submit_body, timeout=300)
        sr.raise_for_status()
        submit = sr.json()
        (OUT / f"submit_{key}.json").write_text(
            json.dumps(submit, indent=2, ensure_ascii=False)
        )

        intent_id = submit.get("intent_id")
        runtime_nest = submit.get("nest_id")
        md = submit.get("metadata") or {}
        gov = md.get("governance_event") or {}
        gov_nest = gov.get("nest_id")

        status = {}
        if intent_id:
            time.sleep(1)
            st = requests.get(f"{BE}/status/{intent_id}", timeout=60)
            if st.ok:
                status = st.json()
                (OUT / f"status_{key}.json").write_text(
                    json.dumps(status, indent=2, ensure_ascii=False)
                )

        gov_extract = {
            "decision": submit.get("decision"),
            "bc_status": submit.get("bc_status"),
            "tx_hash": submit.get("tx_hash") or submit.get("blockchain_tx_hash"),
            "nest_id": runtime_nest,
            "governance_event_nest_id": gov_nest,
            "governance_event_id": gov.get("governance_event_id")
            or md.get("governance_event_id"),
            "lifecycle_state": md.get("lifecycle_state"),
            "decision_score": md.get("decision_score"),
            "match": runtime_nest == gov_nest and runtime_nest is not None,
            "status_nest_id": status.get("nest_id"),
        }
        (OUT / f"governance_{key}.json").write_text(
            json.dumps(gov_extract, indent=2, ensure_ascii=False)
        )
        results[key] = gov_extract
        if not gov_extract["match"]:
            failures.append(key)
        print(f"[E2E] {key}: match={gov_extract['match']} nest={runtime_nest} gov={gov_nest}", flush=True)
        time.sleep(2)

    summary = {"results": results, "failures": failures, "pass": len(failures) == 0}
    (OUT / "e2e_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0 if summary["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
