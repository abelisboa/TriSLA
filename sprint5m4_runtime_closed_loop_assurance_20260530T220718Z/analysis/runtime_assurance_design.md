# Runtime Assurance Design — Sprint 5M4 Phase 2

---

## Target flow

```text
telemetry_snapshot (contract v2)
  ↓ runtime_slo_evaluator.evaluate_runtime_assurance()
  ↓ runtime_assurance_state (COMPLIANT|WARNING|AT_RISK|VIOLATED)
  ↓ runtime_governance_event (on transition only)
  ↓ portal metadata + GET /sla/status
  ↓ Lifecycle Runtime Assurance panel
```

---

## States

| State | Operator meaning |
|-------|------------------|
| COMPLIANT | Metrics within SLA targets |
| WARNING | Approaching limits or minor drift |
| AT_RISK | SLA risk indicators; investigate |
| VIOLATED | SLA breach indicators; escalate (human) |

---

## Outputs

```json
{
  "runtime_assurance": {
    "state": "WARNING",
    "violations": [],
    "warnings": [],
    "drift_detected": true,
    "recommendation": "Monitor transport latency",
    "assurance_state": "WARNING",
    "last_evaluation": "ISO8601",
    "sla_compliance": 0.75,
    "bottleneck_domain": "transport"
  }
}
```

---

## Explicit non-goals

- No Kubernetes / ONOS / Free5GC changes
- No automatic slice reconfiguration
- No Decision Engine score changes
- No blockchain contract changes

---

## Implementation files

| Layer | File |
|-------|------|
| SLA-Agent | `runtime_slo_evaluator.py`, `runtime_assurance_store.py`, `main.py` |
| Portal backend | `sla_status_assurance.py`, `routers/sla.py` |
| Portal frontend | `RuntimeAssurancePanel.tsx`, `runtimeAssurance.ts` |
