#!/usr/bin/env python3
"""Sprint 5M2 E2E — Lifecycle runtime snapshot + pipeline validation."""
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


def snapshot_populated(snap: dict | None) -> bool:
    if not snap or not isinstance(snap, dict):
        return False
    for domain in ("ran", "transport", "core"):
        d = snap.get(domain)
        if isinstance(d, dict) and d:
            return True
    return False


def main() -> int:
    failures = []
    summary = {}

    for key, intent_text, template_id in INTENTS:
        tenant = f"trisla-5m2-{uuid.uuid4().hex[:8]}"
        print(f"[E2E] {key}: interpret …", flush=True)
        ir = requests.post(
            f"{BE}/interpret",
            json={"intent_text": intent_text, "tenant_id": tenant},
            timeout=120,
        )
        ir.raise_for_status()
        interpret = ir.json()

        form_values = build_form_values(interpret)
        form_values["template_id"] = template_id
        sr = requests.post(
            f"{BE}/submit",
            json={"template_id": template_id, "form_values": form_values, "tenant_id": tenant},
            timeout=300,
        )
        sr.raise_for_status()
        submit = sr.json()
        (OUT / f"submit_{key}.json").write_text(json.dumps(submit, indent=2, ensure_ascii=False))

        intent_id = submit.get("intent_id")
        time.sleep(1)
        st = requests.get(f"{BE}/status/{intent_id}", timeout=60)
        st.raise_for_status()
        status = st.json()
        (OUT / f"status_{key}.json").write_text(json.dumps(status, indent=2, ensure_ascii=False))

        submit_snap = (submit.get("metadata") or {}).get("telemetry_snapshot")
        status_snap = status.get("telemetry_snapshot")

        runtime_extract = {
            "intent_id": intent_id,
            "decision": submit.get("decision"),
            "bc_status": submit.get("bc_status"),
            "tx_hash": submit.get("tx_hash"),
            "nest_id": submit.get("nest_id"),
            "governance_event_id": (submit.get("metadata") or {}).get("governance_event_id")
            or ((submit.get("metadata") or {}).get("governance_event") or {}).get("governance_event_id"),
            "governance_event_nest_id": ((submit.get("metadata") or {}).get("governance_event") or {}).get("nest_id"),
            "submit_telemetry_populated": snapshot_populated(submit_snap),
            "status_telemetry_populated": snapshot_populated(status_snap),
            "status_telemetry_snapshot": status_snap,
        }
        (OUT / f"runtime_snapshot_{key}.json").write_text(
            json.dumps(runtime_extract, indent=2, ensure_ascii=False)
        )

        ok = (
            submit.get("decision") == "ACCEPT"
            and submit.get("bc_status") == "COMMITTED"
            and submit.get("tx_hash")
            and submit.get("nest_id")
            and runtime_extract["governance_event_nest_id"] == submit.get("nest_id")
            and runtime_extract["status_telemetry_populated"]
        )
        summary[key] = {**runtime_extract, "pass": ok}
        if not ok:
            failures.append(key)
        print(
            f"[E2E] {key}: status_snapshot={runtime_extract['status_telemetry_populated']} pass={ok}",
            flush=True,
        )
        time.sleep(2)

    out = {"results": summary, "failures": failures, "pass": len(failures) == 0}
    (OUT / "e2e_summary.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return 0 if out["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
