# Runtime Snapshot Binding Audit — Sprint 5M2

**Date:** 2026-05-30T21:54:00Z  
**Classification:** UI + API binding only  
**Root cause validated:** YES (matches Sprint 5M audit)

---

## Data flow map

```text
Lifecycle UI (sla-lifecycle/page.tsx)
  ↓ GET /api/v1/sla/status/{intent_id}
Portal Backend (routers/sla.py → get_sla_status)
  ↓ SEM get_intent + collect_domain_metrics_async
Status API response (SLAStatusResponse)
  ↓ telemetry_snapshot (NEW in 5M2)
LifecycleRuntimeSnapshotPanel
  ↓ lifecycleRuntimeSnapshot.ts field mapping
Runtime Snapshot (RAN / Transport / Core)
```

**Monitoring path (unchanged):**

```text
Monitoring UI
  ↓ GET /api/v1/prometheus/summary + domain endpoints
RAN-I1 / TN-I1 / CN-I1 collectors
  ↓ real Prometheus metrics
Domain cards (PRB, latency, jitter, CPU, memory, …)
```

---

## Audit questions

### 1. Where does Runtime Snapshot read from?

| Layer | Source |
|-------|--------|
| **Before 5M2** | `GET /sla/status/{id}` — no telemetry field; UI showed "Not available" |
| **After 5M2** | `statusData.telemetry_snapshot` from status API, bound in `sla-lifecycle/page.tsx` → `LifecycleRuntimeSnapshotPanel` |

Runtime Supervision (admission) already read `metadata.telemetry_snapshot` from submit response; Lifecycle did not.

### 2. Does submit payload already contain telemetry_snapshot?

**YES.** Submit path in `routers/sla.py` calls `collect_domain_metrics_async()` before decision and stores result in `metadata_out["telemetry_snapshot"]`. Confirmed in 5L/5M evidence and 5M2 E2E (`submit_telemetry_populated: true` for 4/4 intents).

### 3. Does status API expose telemetry_snapshot?

**Before 5M2:** NO — `SLAStatusResponse` had no `telemetry_snapshot` field.  
**After 5M2:** YES — optional `telemetry_snapshot` added to schema; `get_sla_status` resolves via `resolve_status_telemetry_snapshot()`.

### 4. Does portal discard telemetry_snapshot?

**Before 5M2:** Backend discarded it at status boundary (never serialized). Frontend had no binding.  
**After 5M2:** Backend exposes it; frontend maps contract v2 fields only.

### 5. Does Runtime Supervision panel ignore telemetry_snapshot?

**Partially before 5M2:** Submit snapshot was available but status fallback was missing.  
**After 5M2:** `RuntimeSupervisionSection` uses submit snapshot first, status `telemetry_snapshot` as fallback.

### 6. Smallest safe fix

**Priority B (chosen):** Expose `telemetry_snapshot` on existing `GET /sla/status/{id}` using:

1. SEM-persisted `metadata.telemetry_snapshot` (preferred), or
2. Live `collect_domain_metrics_async()` fallback (same collector as submit/monitoring)

**No new endpoints.** No telemetry contract changes. No Prometheus/DE/BC/SEM/SLA-Agent changes.

---

## Implementation files

| Component | File | Change |
|-----------|------|--------|
| Backend schema | `apps/portal-backend/src/schemas/sla.py` | `telemetry_snapshot: Optional[Dict]` on `SLAStatusResponse` |
| Backend resolver | `apps/portal-backend/src/services/sla_status_telemetry.py` | `resolve_status_telemetry_snapshot()` |
| Backend router | `apps/portal-backend/src/routers/sla.py` | Collect + attach on `get_sla_status` |
| Frontend mapping | `apps/portal-frontend/src/lib/lifecycleRuntimeSnapshot.ts` | Contract v2 → display rows |
| Frontend panel | `apps/portal-frontend/src/components/lifecycle/LifecycleRuntimeSnapshotPanel.tsx` | Runtime Snapshot UI |
| Frontend page | `apps/portal-frontend/src/app/sla-lifecycle/page.tsx` | Bind `statusData.telemetry_snapshot` |

---

## Verdict

Root cause **confirmed**. Fix is minimum-change API exposure + UI binding. No architectural changes.
