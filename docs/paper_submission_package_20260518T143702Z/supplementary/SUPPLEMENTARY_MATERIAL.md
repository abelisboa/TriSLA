# TriSLA Supplementary Material

Package: `docs/paper_submission_package_20260518T143702Z`
Digest: `sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6`

## Reproducibility policy
- All reported runtime experiments use a **single pinned** decision-engine image digest.
- Evidence packs are immutable directories with `MANIFEST.txt` and `SHA256SUMS.txt`.
- Do not rebuild or redeploy for artifact evaluation; use copied datasets and freeze snapshots.

## Reviewer-safe taxonomy
- **CAUSAL (admission-time):** score_mode, PRB gates, feasibility, resource_pressure_v1.
- **OPERATIONAL:** NASP instantiate, NCM latency under contention.
- **RECONCILIATORY:** NSI watch, capacity reconciler (no DE callback).
- **PERSISTENT:** SEM SQLite, TriSLAReservation/NSI CRDs, BC submit-time lineage.
- **NON_CAUSAL:** orchestration→admission feedback, continuous autonomous reevaluation, core-driven admission.

## Runtime limitations (explicit negative results)
- No robust tri-slice admission divergence at frozen guards.
- No orchestration-to-decision-engine feedback loop.
- No continuous autonomous reevaluation (SLA-Agent Kafka loop inactive under digest).
- No core-driven admission under contention campaigns.
- No multidomain balanced closed-loop causality.

## Experimental methodology
See `manuscript/TRISLA_CAMERA_READY_MANUSCRIPT.md` Section V and track-specific datasets under `datasets/`.

## Evidence-pack navigation
- `tracks/TRACK_INDEX.md` — program tracks and verdicts
- `freezes/` — per-track runtime_after + summary JSON
- `reports/` — diagnosis, citation audit, approved/forbidden claims
- `figures/` — IEEE figure set from TRACK-03
- `datasets/` — baseline, core, ncm, nad, operational CSVs

## Negative-results rationale
Negative paths are reported as **methodological boundaries**, not experimental failure.
They prevent overclaim and define the roadmap for future closed-loop designs.