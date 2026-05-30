# Non-Regression Proof — Sprint 5M2

**Date:** 2026-05-30T21:54:00Z  
**Baseline references:**

- `sprint5l_runtime_e2e_validation_20260530T193406Z` — SPRINT_5L_RUNTIME_E2E_VALIDATION_APPROVED
- `sprint5m1_governance_nest_propagation_20260530T200758Z` — SPRINT_5M1_GOVERNANCE_NEST_PROPAGATION_APPROVED

---

## Components explicitly unchanged (digest frozen)

| Component | Digest | 5M2 change |
|-----------|--------|------------|
| SEM-CSMF | `sha256:bd0372d6808f005d80f26618154d367ebb856f40daf003601668d8cccab4eaf2` | None |
| Decision Engine | `sha256:47d2679de267d8613b4c01cfaa066aca2374cb80331745f75a14b88845872a37` | None |
| BC-NSSMF | `sha256:b0db5eef…` (5L baseline) | None |
| SLA-Agent | `sha256:3dad23e2…` (5L baseline) | None |
| Prometheus / RAN-I1 / TN-I1 / CN-I1 | SSOT queries unchanged | None |

---

## Functional regression checks (5M2 E2E re-run)

| Check | 5L/5M1 baseline | 5M2 post-deploy | Status |
|-------|-----------------|-----------------|--------|
| Semantic fill (latency/throughput/reliability) | Populated | Submit payloads show filled KPIs | OK |
| Ontology / GST / NEST chain | Operational | Unchanged SEM digest | OK |
| Decision ACCEPT | 4/4 | 4/4 | OK |
| bc_status COMMITTED | 4/4 | 4/4 (retry after transient SKIPPED_ORCH_FAILED) | OK |
| tx_hash present | 4/4 | 4/4 | OK |
| nest_id | 4/4 | 4/4 | OK |
| governance_event.nest_id == nest_id | 5M1 fix | 4/4 match | OK |
| governance_event_id | Present | 4/4 | OK |
| Monitoring summary | Real metrics (5C) | Not redeployed; backend digest change is status-only additive field | OK |
| Telemetry contract v2 | Unchanged shape | `telemetry_contract_version: v2` in snapshots | OK |

---

## Portal change scope (bounded)

| Area | Changed? | Notes |
|------|----------|-------|
| Submit orchestration | No | Same NASP/DE/BC path |
| Prometheus summary endpoint | No | Monitoring queries untouched |
| Semantic resolver | No | SEM digest frozen |
| Decision scoring | No | DE digest frozen |
| Blockchain commit | No | BC digest frozen |
| SLA-Agent revalidate | No | Agent digest frozen |
| Status API | Additive only | New optional `telemetry_snapshot` field |
| Lifecycle UI | Yes | Binds existing snapshot data |
| Runtime Supervision UI | Yes | Status fallback for snapshot display |

---

## Transient anomaly (documented, not M2 regression)

First 5M2 E2E run (21:51Z) hit `bc_status: SKIPPED_ORCH_FAILED` on all 4 intents while telemetry binding succeeded. Immediate 5M1 E2E re-run passed COMMITTED; 5M2 E2E re-run (21:53Z) passed 4/4. Classified as transient NASP orchestration, not caused by portal status/UI binding.

---

## Conclusion

No regression detected in Semantic Fill, Ontology, GST, NEST, Decision Engine, Blockchain, SLA-Agent, Monitoring contracts, or Telemetry Summary. Portal change is additive status field + Lifecycle UI binding only.
