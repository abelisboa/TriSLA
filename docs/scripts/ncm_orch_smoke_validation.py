#!/usr/bin/env python3
"""NCM-EXEC-03 smoke: self-test + dry-run plan validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT))


def main() -> int:
    from ncm_operational_contention_controls import inventory, self_test
    from ncm_orch_campaign import planned_submits, run_ncm_orch_campaign

    st = self_test()
    print("SELF_TEST:", json.dumps(st, indent=2))
    if not all(st.values()):
        return 1
    plan = planned_submits(epochs=3, reps=12)
    print("PLANNED_SUBMITS:", plan)
    if plan != 144:
        print(f"expected 144 planned submits, got {plan}", file=sys.stderr)
        return 1
    out = Path("/tmp/ncm_orch_smoke_dry_run")
    out.mkdir(parents=True, exist_ok=True)
    result = run_ncm_orch_campaign(
        out,
        epochs=3,
        reps=12,
        tenants=4,
        stagger_s=2.0,
        dry_run=True,
    )
    print("DRY_RUN_STATS:", json.dumps(result["stats"], indent=2))
    if not result["stats"].get("n_plan_matches"):
        return 1
    inv = inventory()
    print("INVENTORY_COMPONENTS:", len(inv["components"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
