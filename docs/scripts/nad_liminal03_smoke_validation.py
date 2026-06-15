#!/usr/bin/env python3
"""NAD-EXEC-12: LIMINAL-03 control smoke (self-test + optional single triplet; no full campaign)."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

_SCRIPT = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT))

from nad_boundary_runtime_controls import (  # noqa: E402
    ConcurrentTenantCoordinator,
    ControlVerdict,
    TripletBarrierSynchronizer,
    feasibility_guard,
    liminal03_corridor_enforce,
    pressure_guard,
    pre_triplet_liminal03_validation,
    self_test,
)

SMOKE_TRIPLET = os.getenv("NAD_LIM03_SMOKE_TRIPLET", "0").lower() in ("1", "true", "yes")


def run_smoke(out_dir: Path) -> Dict[str, Any]:
    result: Dict[str, Any] = {"self_test": self_test(), "dry_run_controls": {}}
    coord = ConcurrentTenantCoordinator()
    result["tenant_sample"] = coord.tenant_id("smoke", "24Mbps", 0, 0)
    pg = pressure_guard(resource_pressure=0.42, prb_pct=20.0, sigma_prb_pct=1.2)
    fg = feasibility_guard(feasibility=0.48, score_denominator=0.94)
    result["pressure_guard"] = {"verdict": pg.verdict.value, "reason": pg.reason}
    result["feasibility_guard"] = {"verdict": fg.verdict.value, "reason": fg.reason}
    ce = liminal03_corridor_enforce(
        prb_pct=20.0,
        resource_pressure=0.42,
        feasibility=0.48,
        rtt_ms=12.0,
        decision_score=0.72,
        decision_mode="decision_score",
    )
    result["corridor_enforce"] = {
        "verdict": ce.verdict.value,
        "in_corridor": ce.in_operational_corridor,
        "monitored": ce.monitored,
    }

    if SMOKE_TRIPLET:
        try:
            from nad_liminal_smoke_validation import _health, _query_proxy_prb, _smoke_submit

            if _health():
                from nad_boundary_runtime_controls import TripletSyncState

                sync = TripletBarrierSynchronizer()
                state = TripletSyncState("smoke-rep000", "24Mbps", 0)

                def submit(sl: str, ns: str) -> dict:
                    r = _smoke_submit(sl)
                    return {
                        "decision": r.get("decision"),
                        "decision_score": r.get("decision_score"),
                        "decision_mode": r.get("decision_mode"),
                        "decision_source": "decision_score_mode",
                        "prb_utilization_real": r.get("prb_utilization_real"),
                    }

                state = sync.run_triplet_barrier(state, submit)
                ok, reason = sync.triplet_coherent(state)
                result["optional_triplet"] = {"coherent": ok, "reason": reason, "n_rows": len(state.rows)}
            else:
                result["optional_triplet"] = {"skipped": "backend unhealthy"}
        except Exception as exc:
            result["optional_triplet"] = {"skipped": str(exc)}
    else:
        result["optional_triplet"] = {"skipped": "NAD_LIM03_SMOKE_TRIPLET not set"}

    conv, pg2, fg2, vals = pre_triplet_liminal03_validation(
        lambda: 19.5,
        resource_pressure=0.38,
        feasibility=0.50,
        score_denominator=0.95,
    )
    result["pre_triplet_validation"] = {
        "verdict": conv.value,
        "prb_samples": vals,
        "pressure": pg2.verdict.value,
        "feasibility": fg2.verdict.value,
    }
    (out_dir / "liminal03_smoke_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    print(json.dumps(run_smoke(out), indent=2))
