# TriSLA Metrics Specification (3GPP / ETSI / O-RAN aligned)

## 1. Objective

Define metrics required to validate SLA-aware decision making.

---

## 2. Domain Classification

- Core: Real (free5GC)
- Transport: Real
- RAN: Emulated

---

## 3. Metrics Strategy

Metrics are divided into:

1. Domain metrics (RAN / Transport / Core)
2. SLA-aware metrics
3. ML metrics

---

## 4. RAN Metrics (Emulated)

- PRB utilization (%)
- RAN throughput (Mbps)
- Packet loss (%)
- Scheduling delay (ms)

Note: values derived from simulation models.

---

## 5. Transport Metrics (Real)

- RTT (ms)
- Jitter (ms)
- Packet loss (%)
- Bandwidth utilization

---

## 6. Core Metrics (Real)

- CPU usage per NF
- Memory usage
- Active sessions
- Session setup time

---

## 7. SLA-aware Metrics

- SLA satisfaction ratio
- SLA violation rate
- Admission accuracy
- False accept rate

---

## 8. ML Metrics

- Risk score distribution
- Class probabilities
- Confidence score

---

## 9. Storage Model

All metrics must be stored per request:

{
  execution_id,
  slice_type,
  ran: {...},
  transport: {...},
  core: {...}
}

---

## 10. Scientific Requirement

Only SUCCESS executions must be used for analysis.
