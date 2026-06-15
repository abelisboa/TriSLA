#!/usr/bin/env python3
"""CORE-EXEC-06 smoke: self-test + dry-run campaign (no live traffic)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT))


def main() -> int:
    from core_contention_runtime_controls import inventory, self_test
    from core_contention_campaign import run_core_contention_campaign

    st = self_test()
    print("SELF_TEST:", json.dumps(st, indent=2))
    if not all(st.values()):
        return 1
    out = Path("/tmp/core_contention_smoke_dry_run")
    out.mkdir(parents=True, exist_ok=True)
    result = run_core_contention_campaign(out, n_reps=2, dry_run=True)
    print("DRY_RUN_STATS:", json.dumps(result["stats"], indent=2))
    inv = inventory()
    print("INVENTORY_COMPONENTS:", len(inv["components"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
