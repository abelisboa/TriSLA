# SLO Inventory — Sprint 5M4 Phase 1

---

## RAN KPIs (contract v2)

| KPI | Source field | Evaluable | Threshold source | Drift support |
|-----|--------------|-----------|------------------|---------------|
| PRB utilization | `ran.prb_utilization` | Yes | SLICE_THRESHOLDS / SLO yaml | Yes (delta) |
| Radio load | `ran.latency_ms`, `ran.latency` | Yes | URLLC latency thresholds | Yes |

---

## Transport KPIs

| KPI | Source field | Evaluable | Threshold source | Drift support |
|-----|--------------|-----------|------------------|---------------|
| RTT / Latency | `transport.rtt_ms`, `rtt` | Yes | TN-I1 + slice thresholds | Yes |
| Jitter | `transport.jitter_ms`, `jitter` | Yes | SLO yaml / P2 thresholds | Yes |
| Throughput | `transport.throughput_mbps` | Yes (when present) | Service profile + EMBB thresholds | Partial |

---

## Core KPIs

| KPI | Source field | Evaluable | Threshold source | Drift support |
|-----|--------------|-----------|------------------|---------------|
| CPU | `core.cpu`, `core.cpu_utilization` | Yes | CN-I1 / slice thresholds | Yes |
| Memory | `core.memory`, `core.memory_utilization` | Yes | Slice thresholds | Relative delta |
| Sessions | `core.sessions`, `active_sessions` | When exported | MMTC core thresholds | No (display only) |

---

## Service Profile KPIs

| KPI | Source | Evaluable | Normalization |
|-----|--------|-----------|---------------|
| Latency | `sla_requirements.latency` | Yes | Parse `10ms` → float |
| Throughput | `sla_requirements.throughput` | Yes | Parse `100Mbps` → float |
| Reliability | `sla_requirements.reliability` | When telemetry present | Percent / ratio |

---

## State mapping (deterministic)

| State | Condition |
|-------|-----------|
| COMPLIANT | No violations; sla_compliance ≥ 0.85; no warnings |
| WARNING | Borderline compliance or warnings |
| AT_RISK | Single violation or low compliance |
| VIOLATED | Multiple violations or compliance < 0.50 |

No ML. No AI inference.
