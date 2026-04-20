# TriSLA Observability (SSOT)

Observability in TriSLA is a cross-cutting architectural capability designed to expose internal system behavior, enable auditability, and support reproducibility.

---

## 1. Scope

Observability provides:

- Metrics (Prometheus)
- Traces (OpenTelemetry)
- Logs (structured logging)

---

## 2. Observability Model

TriSLA observability is based on:

- correlation identifiers (intent_id, decision_id, sla_id)
- end-to-end traceability
- evidence-based metrics

---

## 3. Domain Causal Metrics

### RAN
- PRB utilization (%)
- latency (ms)
- jitter (ms)
- reliability (%)

### Transport
- throughput (Mbps)
- packet loss (%)

### Core
- CPU utilization (%)
- memory utilization (%)
- availability (%)

---

## 4. SLA Mapping

| Slice | Dominant Domain |
|------|----------------|
| URLLC | RAN |
| eMBB | Transport |
| mMTC | Core |

---

## 5. Metrics Stack

- Prometheus
- OpenTelemetry
- Grafana (optional)

---

## 6. Traceability

Each request propagates:

- intent_id
- decision_id
- trace_id

---

## 7. Decision Flow Observability

SEM-CSMF → ML-NSMF → Decision Engine → BC-NSSMF → SLA-Agent

---

## 8. Observability Guarantees

- does not alter decision logic
- full pipeline traceability
- reproducible signals

---

## 9. Troubleshooting Signals

- missing metrics → Prometheus config
- missing traces → OTEL collector
- inconsistent IDs → propagation issue

---

## 10. Installation Reference

→ ../INSTALLATION.md
