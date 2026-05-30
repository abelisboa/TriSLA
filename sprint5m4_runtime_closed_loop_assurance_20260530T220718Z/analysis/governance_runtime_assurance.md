# Governance Runtime Assurance — Sprint 5M4 Phase 4

---

## Event category (additive)

| Field | Value |
|-------|-------|
| `event_type` | `RUNTIME_ASSURANCE` |
| `event_category` | `runtime_assurance_state_change` |
| `authority` | `sla-agent-runtime-assurance` |
| `blockchain_scope` | `none` |

---

## Trigger

State transition only:

```text
COMPLIANT → WARNING → AT_RISK → VIOLATED
```

(and reverse transitions if metrics improve)

---

## Unchanged

- Admission `governance_event` from Decision Engine
- `tx_hash` / BC-NSSMF registration path
- On-chain contracts

---

## Example event

```json
{
  "governance_event_id": "ge_runtime_…",
  "event_type": "RUNTIME_ASSURANCE",
  "event_state": "VIOLATED",
  "previous_state": "COMPLIANT",
  "source": "sla-agent-layer",
  "blockchain_scope": "none",
  "recommendation": "Escalate …"
}
```

Stored in submit `metadata.runtime_governance_event` when transition occurs.

Unit test: `test_governance_event_on_transition` PASS.
