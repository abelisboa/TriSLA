# TriSLA — operating rules (governance v2)

These rules apply to humans and automation (CI, agents) working on TriSLA. They exist to **preserve a known-good runtime** and avoid silent regressions.

---

## WORKDIR

| Context | Path |
|--------|------|
| Development / evidence / collection | `trisla/` (this repository root) |
| Publication / public mirror (when used) | `trisla_public/` |

Use the repository SSOT for scripts and docs; do not scatter “second copies” of runbooks outside the agreed tree without updating indexes under `docs/RECOVERED/`.

---

## INVESTIGATION

1. **Never alter before investigating** — reproduce, capture logs, identify blast radius.
2. **Never alter without evidence** — link commands, timestamps, and artifacts (snapshots, JSON responses).
3. Prefer **read-only** inspection (`kubectl get`, `curl`, logs) before any mutating command.

---

## AUTHORIZATION

- **No change** to application code, Helm charts, Kubernetes workloads, blockchain configuration, or SLA-Agent configuration **without explicit authorization** from the responsible operator or documented change ticket.
- “Looks wrong” is not authorization. Telemetry gaps, in particular, are **not** automatic permission to patch PromQL or deployments.

---

## RUNBOOK

- **`docs/TRISLA_MASTER_RUNBOOK.md`** is the **operational source of truth** for end-to-end behaviour, history, and validated procedures.
- Cross-check specialised canons when touching a subsystem:
  - `docs/TRISLA_E2E_FLOW_CANONICAL.md`
  - `docs/TRISLA_BLOCKCHAIN_CANONICAL.md`
  - `docs/TRISLA_INFRA_SSOT.md` (declared cluster / portal-backend configuration snapshots)
  - `docs/nasp/NASP_DEPLOY_RUNBOOK.md` (NASP-specific)
- If live cluster state **diverges** from the runbook, **document the divergence** first; do not “fix” silently.

---

## INTERPRETATION (current baseline)

- **Functional pipeline** (BC committed, SLA-Agent OK, NASP success) does **not** imply “change nothing forever”; it implies **do not destabilize** what is proven without authorization and evidence.
- **Partial telemetry** is a **documented gap**, not an emergency override for the governance rules above.
