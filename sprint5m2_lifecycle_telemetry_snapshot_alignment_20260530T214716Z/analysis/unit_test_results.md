# Unit Test Results — Sprint 5M2

**Date:** 2026-05-30T21:54:00Z  
**Commit:** `fe65899708bf4a535c90db96b6d85395abac0d09`

---

## Portal Backend — `test_status_telemetry_snapshot.py`

**Command:** `pytest apps/portal-backend/tests/test_status_telemetry_snapshot.py -v`

| Test | Slice | Assertion | Result |
|------|-------|-----------|--------|
| `test_urllc_domains_populated` | URLLC | RAN/Transport/Core rows resolvable | PASS |
| `test_embb_domains_populated` | eMBB | RAN/Transport/Core rows resolvable | PASS |
| `test_mmtc_domains_populated` | mMTC | RAN/Transport/Core rows resolvable | PASS |
| `test_smartcity_domains_populated` | Smart City | RAN/Transport/Core rows resolvable | PASS |
| `test_prefers_sem_metadata_snapshot` | — | SEM metadata snapshot preferred over collect | PASS |
| `test_falls_back_to_collected_snapshot` | — | Live collect used when SEM snapshot absent | PASS |

**Summary:** 6/6 passed (0.20s)

---

## Portal Frontend — `test-lifecycle-runtime-snapshot.mjs`

**Command:** `node apps/portal-frontend/scripts/test-lifecycle-runtime-snapshot.mjs`

| Scenario | Runtime Snapshot populated | Telemetry fields present | Result |
|----------|---------------------------|--------------------------|--------|
| URLLC | Yes | PRB, Radio Load, Latency, Jitter, CPU, Memory | PASS |
| eMBB | Yes | PRB, Radio Load, Latency, Jitter, CPU, Memory | PASS |
| mMTC | Yes | PRB, Radio Load, Latency, Jitter, CPU, Memory | PASS |
| Smart City | Yes | PRB, Radio Load, Latency, Jitter, CPU, Memory | PASS |

**Summary:** 4/4 passed

---

## Assertions covered

- Runtime Snapshot populated when contract v2 snapshot present
- Telemetry fields mapped from existing keys only (no synthetic values)
- No null-domain display when snapshot contains domain data
- Status resolver prefers persisted SEM snapshot over live collect

**Overall:** 10/10 unit tests PASS
