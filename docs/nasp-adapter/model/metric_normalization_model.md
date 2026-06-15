# Metric Normalization Model

> Operational metrics endpoints: [`docs/modules/nasp-adapter.md`](../../modules/nasp-adapter.md).
> Observability detail: [`observability/observability.md`](../observability/observability.md).

## 1. Objective

Transform heterogeneous infrastructure signals (RAN, transport, core) into a **unified multidomain representation** suitable for feasibility checks, capacity accounting, and Portal telemetry composition.

## 2. Input Domains

```text
M = (M_ran, M_transport, M_core)
```

| Domain | Sources (implementation) |
|--------|--------------------------|
| RAN | NASP RAN metrics endpoint; PRB via `metrics_collector.py` |
| Transport | Prometheus probes; ONOS snapshot (O5C) |
| Core | Prometheus container metrics; Free5GC AMF/SMF probes |

## 3. MDCE Export Schema

Primary structured export: `GET /api/v1/metrics/multidomain`

Implemented in `metrics_collector.get_multidomain()` — aligns with MDCE SSOT schema (`docs/MDCE_SCHEMA.json` reference in code).

Fields include core CPU/memory, RAN UE count proxy, transport RTT, and `reasons[]` for unavailable metrics (null-safe).

## 4. Normalization Approach

Operational normalization (not a single min-max formula on all fields):

- Prometheus scalar extraction with null on failure
- MDCE field mapping with explicit `reasons` when unavailable
- PRB exported as percent `[0, 100]` via `trisla_ran_prb_utilization` gauge
- Capacity ledger consumes multidomain snapshot at instantiate time

Legacy generic formula \(m_{norm} = (m - m_{min}) / (m_{max} - m_{min})\) applies to analytical modeling only; runtime uses schema-driven MDCE mapping.

## 5. Consumers (runtime truth)

| Consumer | Path | Notes |
|----------|------|-------|
| **Portal Backend** | Telemetry collector / submit flow | Primary consumer of multidomain context |
| **Capacity accounting** | Pre-instantiate in `main.py` | Uses `get_multidomain()` for ledger check |
| **Prometheus scrapers** | `/metrics`, PRB gauge | Observability and cross-module Prom queries |
| **SEM-CSMF** | Indirect via Portal Prom proxy | PRB resolution in `decision_engine_client.py` |

Decision Engine does **not** consume NASP Adapter metrics via a direct HTTP API in the production admission path. DE receives `telemetry_snapshot` composed upstream (Portal / SEM enrichment).

## 6. Importance

Consistent multidomain representation enables capacity accounting before NSI creation and supports reproducible validation campaigns without coupling admission logic to infrastructure adapters.

## 7. Conclusion

The NASP Adapter normalizes infrastructure metrics into MDCE-aligned structures. Consumption flows through Portal and capacity subsystems, preserving the frozen admission boundary.
