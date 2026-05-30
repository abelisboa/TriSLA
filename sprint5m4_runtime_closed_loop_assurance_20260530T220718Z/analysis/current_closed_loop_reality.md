# Current Closed-Loop Reality — Sprint 5M4 Phase 0

**Date:** 2026-05-30T22:12:00Z  
**Baseline:** Sprint 5M audit + 5M2 telemetry alignment

---

## Pipeline map (pre-5M4)

```text
Portal submit
  ↓ NASP (SEM → DE → BC)
  ↓ telemetry_snapshot collected (portal-backend)
  ↓ SLA-Agent POST /api/v1/ingest/pipeline-event
  ↓ pipeline_ingested=true (audit only)
  ↓ Lifecycle COMPLETED
```

**Gap (5M audit):** No SLO evaluation loop, no drift→governance path, manual revalidate only.

---

## Audit answers

| # | Question | Pre-5M4 | Post-5M4 |
|---|----------|---------|----------|
| 1 | Where telemetry enters | Portal `collect_domain_metrics_async`; contract v2 snapshot in submit metadata | Unchanged |
| 2 | What SLA-Agent stores | In-memory pipeline log; optional SLO yaml eval if `run_slo_evaluation=true` | Adds `runtime_assurance` evaluation + transition store |
| 3 | Events generated | Pipeline ingest log; revalidate drift (manual) | Additive `RUNTIME_ASSURANCE` governance events on state change |
| 4 | Thresholds exist | `domain_compliance.py` SLICE_THRESHOLDS; SLO yaml configs; P2 drift env thresholds | Reused deterministically in `runtime_slo_evaluator.py` |
| 5 | Telemetry available | RAN/Transport/Core contract v2 + service profile KPIs | Unchanged |
| 6 | APIs reused | `/ingest/pipeline-event`, `/agent/revalidate-telemetry`, `/sla/status` | Extended ingest; new `/runtime-assurance/evaluate`; status exposes `runtime_assurance` |

---

## Components unchanged

Decision Engine, BC-NSSMF, SEM-CSMF, Prometheus collectors, score formula.

---

## 5M4 scope

Observation + revalidation + governance event registration + portal display. **No autonomous remediation.**
