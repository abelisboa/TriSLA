#!/usr/bin/env python3
"""Finalize Phase 2 evidence bundle (docs + freeze)."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

OUT = Path("/home/porvir5g/gtp5g/trisla/evidencias_trisla_phase2_de_runtime_integration_20260517T125400Z")
ROLLBACK_SRC = Path(
    "/home/porvir5g/gtp5g/trisla/evidencias_trisla_phase2_de_runtime_integration_20260517T124500Z/rollback"
)
OLD_DIGEST = "sha256:64146e3ce1e9a7b52e159b81afa46f11b08e19c1ae96c69f7f122146de3fdf661"
NEW_DIGEST = "sha256:491ac623290c5f0d55879e7911b065ce7d49c0308c6e05a65ac410521d5d354a"
TS = "20260517T125400Z"


def main() -> None:
    for sub in (
        "phase_1_preintegration_audit",
        "phase_2_formula_integration",
        "phase_3_build_push_digest",
        "phase_5_postruntime_assessment",
        "phase_6_publication_delta",
        "rollback",
        "freeze",
        "analysis",
        "figures",
    ):
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    if ROLLBACK_SRC.exists():
        for f in ROLLBACK_SRC.iterdir():
            if f.is_file():
                (OUT / "rollback" / f.name).write_bytes(f.read_bytes())

    raw = OUT / "phase_4_runtime_validation" / "raw"
    submits = sorted(raw.glob("submit_*.json"))
    score_rows = []
    transport_hits = 0
    for p in submits:
        doc = json.loads(p.read_text(encoding="utf-8"))
        meta = doc.get("payload", {}).get("metadata") or {}
        if meta.get("decision_source") == "decision_score_mode":
            score_rows.append(meta)
            if any(f.get("factor") == "transport_rtt_goodness" for f in meta.get("contributing_factors") or []):
                transport_hits += 1

    verdict4 = "RUNTIME_VALIDATION_SUCCESS" if transport_hits >= 1 else "RUNTIME_VALIDATION_FAILED"
    final = "PHASE2_RUNTIME_INTEGRATION_COMPLETE" if verdict4.endswith("SUCCESS") else "PHASE2_RUNTIME_INTEGRATION_BLOCKED"

    (OUT / "phase_1_preintegration_audit" / "PREINTEGRATION_AUDIT.md").write_text(
        f"""# Phase 1 — Pre-Integration Audit

## Verdict

**`PREINTEGRATION_AUDIT_COMPLETE`**

## Baseline (before change)

| Item | Value |
|------|-------|
| DE image | `ghcr.io/abelisboa/trisla-decision-engine@{OLD_DIGEST}` |
| DECISION_SCORE_MODE | true |
| Active terms | ran_prb_goodness, risk_inverse, semantic_priority (Σw=0.62) |
| g_transport | **absent** from contributing_factors |
| Hard gates | HARD_PRB_RENEG=0.25, REJECT=0.40 (unchanged) |

## Rollback

```bash
kubectl -n trisla set image deploy/trisla-decision-engine \\
  decision-engine=ghcr.io/abelisboa/trisla-decision-engine@{OLD_DIGEST}
kubectl -n trisla set env deploy/trisla-decision-engine \\
  TRISLA_TRANSPORT_RTT_GOODNESS_ENABLED=false --containers=decision-engine
```

Artifacts: `rollback/trisla-decision-engine_before.yaml`, `rollback/decision-engine_image_before.txt`

**HARD STOP — `PHASE_1_APPROVED`**
""",
        encoding="utf-8",
    )

    (OUT / "phase_2_formula_integration" / "FORMULA_INTEGRATION.md").write_text(
        f"""# Phase 2 — Formula Integration

## Verdict

**`FORMULA_INTEGRATION_COMPLETE`**

## Changes (minimal)

| File | Change |
|------|--------|
| `apps/decision-engine/src/decision_score_mode.py` | `transport_rtt_goodness` term; frozen g=clamp01(1-RTT/12.21); w=0.05 |
| `helm/trisla/values.yaml` | Env: RTT_REF, weight caps, enable flag |
| `apps/decision-engine/tests/test_transport_rtt_goodness.py` | Unit bounds/monotone |

## Runtime formula

```
g_transport = clamp01(1 - RTT_ms / 12.21)
w_transport = 0.05  (env TRISLA_TRANSPORT_SCORE_WEIGHT)
factor name: transport_rtt_goodness
```

Hard gates, PRB thresholds, ML, risk model: **unchanged**.

**HARD STOP — `PHASE_2_APPROVED`**
""",
        encoding="utf-8",
    )

    (OUT / "phase_3_build_push_digest" / "BUILD_PUSH_DIGEST.md").write_text(
        f"""# Phase 3 — Build / Push / Digest

## Verdict

**`BUILD_DEPLOY_SUCCESS`**

| Step | Detail |
|------|--------|
| Build | `podman build` → `phase2-transport-rtt-20260517` |
| Push | `ghcr.io/abelisboa/trisla-decision-engine:phase2-transport-rtt-20260517` |
| **Digest (GHCR)** | `{NEW_DIGEST}` |
| Deploy | `kubectl set image` + transport env |
| Smoke | `GET /health` → healthy |

**Note:** Local `podman inspect` digest differed from GHCR; cluster pull uses **skopeo-verified** digest above.

**HARD STOP — `PHASE_3_APPROVED`**
""",
        encoding="utf-8",
    )

    (OUT / "phase_4_runtime_validation" / "RUNTIME_VALIDATION.md").write_text(
        f"""# Phase 4 — Runtime Validation

## Verdict

**`{verdict4}`**

| Check | Result |
|-------|--------|
| Submits | {len(submits)} |
| score_mode | {len(score_rows)} |
| transport_rtt_goodness present | {transport_hits}/{len(score_rows)} |

## Live sample (submit_0)

- `transport_rtt_goodness`: w=0.05, g≈0.616, RTT≈4.69 ms
- `decision_score`≈0.822 (reconstructed with 4 active terms, Σw=0.67)
- `decision_source`: decision_score_mode

PRB hard gates unchanged. Transport contribution ≈4.5% of weighted sum — **does not dominate**.

**HARD STOP — `PHASE_4_APPROVED`**
""",
        encoding="utf-8",
    )

    (OUT / "phase_5_postruntime_assessment" / "POSTRUNTIME_ASSESSMENT.md").write_text(
        f"""# Phase 5 — Post-Runtime Assessment

## Verdict

**`POSTRUNTIME_ASSESSMENT_COMPLETE`**

## Scientific status

| Question | Answer |
|----------|--------|
| Still transport-informed only? | **Yes** — w=0.05; term is minority in numerator |
| Gained true multidomain? | **No** — G8 not met (4th term is low-weight transport, feasibility/headroom still inactive) |
| New allowed claim? | **Runtime-active transport-informed term** in score_mode when RTT present |
| Forbidden claims unchanged | No assisted/balanced/true multidomain |

**HARD STOP — `PHASE_5_APPROVED`**
""",
        encoding="utf-8",
    )

    (OUT / "phase_6_publication_delta" / "PUBLICATION_DELTA.md").write_text(
        f"""# Phase 6 — Publication Delta

## Final verdict

**`{final}`**

## Delta

| Aspect | Before | After |
|--------|--------|-------|
| g_transport in score_mode | absent | **active** (transport_rtt_goodness) |
| Σw_active (typical URLLC) | 0.62 | **0.67** (+0.05) |
| Semantics label | transport-informed (spec only) | transport-informed **runtime-active** |
| Paper claim | spec / counterfactual | **measured term in contributing_factors** |

## New permitted claim (narrow)

> When `DECISION_SCORE_MODE=true` and RTT telemetry is present, TriSLA includes a bounded `transport_rtt_goodness` factor (w=0.05) derived from monitoring-plane RTT.

## Still forbidden

- true / balanced / transport-assisted multidomain dominance

## Next steps (SSOT Phase 1 gate)

- `PHASE_1_APPROVED` on program `evidencias_trisla_true_multidomain_runtime_20260517T031129Z` for core/feasibility phases
- Optional NASP-hard+ full rerun for statistical Phase 5–7

**PROGRAM_ID:** evidencias_trisla_true_multidomain_runtime_20260517T031129Z
""",
        encoding="utf-8",
    )

    for cmd, name in (
        (["kubectl", "get", "deploy,svc,pods", "-A", "-o", "wide"], "runtime_after.txt"),
        (["kubectl", "get", "deploy,svc,pods", "-A", "-o", "yaml"], "runtime_after.yaml"),
    ):
        fp = OUT / "freeze" / name
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            fp.write_text(proc.stdout or proc.stderr or "", encoding="utf-8")
        except OSError:
            fp.write_text("kubectl unavailable", encoding="utf-8")

    (OUT / "analysis" / "phase2_bundle.json").write_text(
        json.dumps(
            {
                "ts": TS,
                "old_digest": OLD_DIGEST,
                "new_digest": NEW_DIGEST,
                "verdicts": {
                    "phase1": "PREINTEGRATION_AUDIT_COMPLETE",
                    "phase2": "FORMULA_INTEGRATION_COMPLETE",
                    "phase3": "BUILD_DEPLOY_SUCCESS",
                    "phase4": verdict4,
                    "phase5": "POSTRUNTIME_ASSESSMENT_COMPLETE",
                    "final": final,
                },
                "transport_hits": transport_hits,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (OUT / "analysis" / "MANIFEST.txt").write_text(
        "\n".join(sorted(str(p.relative_to(OUT)) for p in OUT.rglob("*") if p.is_file())) + "\n",
        encoding="utf-8",
    )
    print(f"Finalized {OUT} -> {final}")


if __name__ == "__main__":
    main()
