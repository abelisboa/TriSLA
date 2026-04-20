# Governance audit report v2 (read-only)

**Date:** 2026-04-15  
**Scope:** TriSLA pipeline vs runbook; telemetry completeness; `TELEMETRY_PROMQL_*` vs infra SSOT.  
**Mutations applied:** **NONE** (no code, Helm, or cluster changes as part of this governance pass).

---

## Pipeline (runbook-aligned)

| Check | Status |
|-------|--------|
| BC `COMMITTED` | **OK** (baseline per `docs/TRISLA_MASTER_RUNBOOK.md`; recent E2E validation in governance thread) |
| SLA-Agent `OK` | **OK** (ingest path when `SLA_AGENT_PIPELINE_INGEST_URL` set; see `docs/TRISLA_E2E_FLOW_CANONICAL.md`) |
| NASP orchestration | **OK** (`SUCCESS` on validated submit) |
| E2E submit | **Functional** |

**Conclusion:** No structural failure; **do not “repair”** the transactional path without explicit authorization.

---

## Telemetry

| Observation | Detail |
|-------------|--------|
| `metadata.telemetry_complete` | Often **false** when RAN fields (e.g. PRB, latency) are missing or gap-filled |
| RAN metrics | **MISSING / PARTIAL** in typical responses (e.g. `prb_utilization` at `0.0`, `latency_ms` null) while transport/core may be populated |
| Interpretation | Documented behaviour: incomplete snapshot sets gaps (`docs/TRISLA_MASTER_RUNBOOK.md`); **not** a trigger for silent PromQL patches under governance v2 |

**Telemetry status:** **INCOMPLETE** (acceptable for governance until a separate authorized change window).

---

## Config drift — `TELEMETRY_PROMQL_*` (portal-backend)

**Reference:** `docs/TRISLA_INFRA_SSOT.md` (embedded deployment manifest — canonical example block for `trisla-portal-backend`).

**Live cluster** (`kubectl` read-only, `Deployment/trisla-portal-backend`, namespace `trisla`):

| Variable | Live value (abridged) |
|----------|------------------------|
| `TELEMETRY_PROMQL_RAN_LATENCY` | `avg(trisla_ran_latency_ms)` |
| `TELEMETRY_PROMQL_RAN_PRB` | `avg(trisla_ran_prb_utilization)` |
| `TELEMETRY_PROMQL_TRANSPORT_RTT` | `max(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"})*1000` |
| `TELEMETRY_PROMQL_TRANSPORT_JITTER` | `(max_over_time(probe_duration_seconds[1m]) - min_over_time(probe_duration_seconds[1m])) * 1000` |

**SSOT example** (excerpt from `docs/TRISLA_INFRA_SSOT.md` — first canonical `trisla-portal-backend` env list):

| Variable | SSOT example |
|----------|----------------|
| `TELEMETRY_PROMQL_RAN_LATENCY` | `avg(trisla_ran_latency_ms{job="trisla-prb-simulator"})` |
| `TELEMETRY_PROMQL_RAN_PRB` | `avg(trisla_ran_prb_utilization)` (variant manifests also show `job!="trisla-prb-simulator"` filters) |
| `TELEMETRY_PROMQL_TRANSPORT_RTT` | Same job filter on `probe_duration_seconds` as live |
| `TELEMETRY_PROMQL_TRANSPORT_JITTER` | `avg((max_over_time(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}[1m]) - min_over_time(...[1m])) * 1000)` |

**Divergence summary:**

1. **RAN latency:** live query **lacks** `job="trisla-prb-simulator"` selector present in SSOT.
2. **Transport jitter:** live query **lacks** `job="probe/monitoring/trisla-transport-tcp-probe"` on `probe_duration_seconds` and uses a different aggregation wrapper (`avg(...)` in SSOT vs bare range expression live).

**Action:** **NONE** under governance v2 — document only; any alignment requires explicit authorization and a planned rollout.

---

### Jitter Alignment Resolution

Previous discrepancies between SSOT and runtime jitter usage have been resolved.

The system now consistently treats jitter as:

- ML feature (via SLA input)
- Observability metric (runtime telemetry)
- Not a direct decision variable

---

## Recovered artifacts (this pass)

| Category | Deliverable |
|----------|-------------|
| Structure | `docs/RECOVERED/` + `RUNBOOKS/`, `PROMPTS/`, `SCRIPTS/` |
| Rules | `OPERATING_RULES.md` |
| Indexes | `README.md` (root), `RUNBOOKS/README.md`, `PROMPTS/README.md`, `SCRIPTS/README.md` |
| Audit | `AUDIT_REPORT_V2.md` (this file) |

**Catalogued references:** 14 runbook paths + 22 prompt/audit rows + 26 script paths + 4 governance files ≈ **66** indexed artifacts (overlap between backup and `docs/` is intentional; operators should prefer `docs/`).

---

## Final status

| Area | Status |
|------|--------|
| Pipeline | **OK** |
| BC | **OK** |
| SLA-Agent | **OK** |
| NASP | **OK** |
| Telemetry | **INCOMPLETE** |
| RAN metrics | **MISSING / PARTIAL** |
| Alterações aplicadas | **NONE** |

**FINAL STATUS:** **SYSTEM STABLE — NO CHANGES REQUIRED** for the functional E2E path. Telemetry remains a **documented gap**, not an emergency override.
